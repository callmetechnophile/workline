output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.workline_vpc.id
}

output "kms_key_arn" {
  description = "Customer Managed KMS Key ARN"
  value       = aws_kms_key.workline_key.arn
}

output "artifacts_bucket_name" {
  description = "S3 Artifacts Bucket Name"
  value       = aws_s3_bucket.artifacts.id
}

output "sqs_queue_url" {
  description = "SQS Main Task Queue URL"
  value       = aws_sqs_queue.jobs_queue.url
}

output "sqs_dlq_url" {
  description = "SQS Dead Letter Queue URL"
  value       = aws_sqs_queue.jobs_dlq.url
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.workline_pool.id
}

output "cognito_app_client_id" {
  description = "Cognito Web Client ID"
  value       = aws_cognito_user_pool_client.web_client.id
}
