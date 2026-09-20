terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Workline"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ------------------------------------------------------------------------------
# 1. KMS Customer Managed Key
# ------------------------------------------------------------------------------
resource "aws_kms_key" "workline_key" {
  description             = "Workline Master Encryption Key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "workline_key_alias" {
  name          = "alias/workline-${var.environment}"
  target_key_id = aws_kms_key.workline_key.key_id
}

# ------------------------------------------------------------------------------
# 2. Virtual Private Cloud (VPC) & Multi-AZ Subnets
# ------------------------------------------------------------------------------
resource "aws_vpc" "workline_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "workline-vpc-${var.environment}"
  }
}

resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.workline_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "workline-public-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "Public"
  }
}

resource "aws_subnet" "private_app" {
  count             = 3
  vpc_id            = aws_vpc.workline_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "workline-private-app-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "PrivateApp"
  }
}

resource "aws_subnet" "isolated_data" {
  count             = 3
  vpc_id            = aws_vpc.workline_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "workline-isolated-data-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "IsolatedData"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.workline_vpc.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.workline_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public" {
  count          = 3
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "isolated" {
  vpc_id = aws_vpc.workline_vpc.id
  tags = {
    Name = "workline-isolated-rt-${var.environment}"
  }
}

resource "aws_route_table_association" "isolated" {
  count          = 3
  subnet_id      = aws_subnet.isolated_data[count.index].id
  route_table_id = aws_route_table.isolated.id
}

# ------------------------------------------------------------------------------
# 3. Amazon S3 Artifacts Bucket
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "artifacts" {
  bucket        = "workline-artifacts-${var.environment}-${var.aws_account_id}"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.workline_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------------------------------------------------------
# 4. Amazon SQS Job Queues (Standard + DLQ)
# ------------------------------------------------------------------------------
resource "aws_sqs_queue" "jobs_dlq" {
  name                      = "workline-jobs-dlq-${var.environment}"
  message_retention_seconds = 1209600
  kms_master_key_id         = aws_kms_key.workline_key.arn
}

resource "aws_sqs_queue" "jobs_queue" {
  name                       = "workline-jobs-${var.environment}"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 345600
  kms_master_key_id          = aws_kms_key.workline_key.arn

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn
    maxReceiveCount     = 3
  })
}

# ------------------------------------------------------------------------------
# 5. Amazon Cognito User Pool
# ------------------------------------------------------------------------------
resource "aws_cognito_user_pool" "workline_pool" {
  name = "workline-user-pool-${var.environment}"

  password_policy {
    minimum_length    = 10
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  auto_verified_attributes = ["email"]
}

resource "aws_cognito_user_pool_client" "web_client" {
  name         = "workline-web-client-${var.environment}"
  user_pool_id = aws_cognito_user_pool.workline_pool.id

  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

# ------------------------------------------------------------------------------
# 6. Security Groups
# ------------------------------------------------------------------------------
resource "aws_security_group" "alb" {
  name        = "workline-alb-sg-${var.environment}"
  description = "Ingress from CloudFront/Internet to ALB"
  vpc_id      = aws_vpc.workline_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "app_tasks" {
  name        = "workline-app-tasks-sg-${var.environment}"
  description = "Ingress for ECS API and Worker tasks"
  vpc_id      = aws_vpc.workline_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "isolated_data" {
  name        = "workline-isolated-data-sg-${var.environment}"
  description = "Strict ingress to SurrealDB, Qdrant, and Redis from App tasks ONLY"
  vpc_id      = aws_vpc.workline_vpc.id

  # SurrealDB on port 8000
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tasks.id]
  }

  # Qdrant on ports 6333 & 6334
  ingress {
    from_port       = 6333
    to_port         = 6334
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tasks.id]
  }

  # Redis on port 6379
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tasks.id]
  }
}

# ------------------------------------------------------------------------------
# 7. ECS Cluster & Fargate Services
# ------------------------------------------------------------------------------
resource "aws_ecs_cluster" "workline_cluster" {
  name = "workline-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}
