import json
import subprocess
import urllib.request
import urllib.error

aws_cli = r"C:\Program Files\Amazon\AWSCLIV2\aws.exe"

# 1. Get Cognito token
print("Authenticating test user with AWS Cognito...")
cmd = [
    aws_cli, "cognito-idp", "admin-initiate-auth",
    "--user-pool-id", "us-east-1_AFlRukzzO",
    "--client-id", "5itdpbhrcp4dd5569sj1p3eefm",
    "--auth-flow", "ADMIN_NO_SRP_AUTH",
    "--auth-parameters", "USERNAME=testuser@workline.ai,PASSWORD=WorklineDev123!",
    "--region", "us-east-1"
]
res = subprocess.run(cmd, capture_output=True, text=True, check=True)
auth_data = json.loads(res.stdout)
id_token = auth_data["AuthenticationResult"]["IdToken"]
print("Cognito authentication successful! Token obtained.")

base_url = "https://n70vojh6j7.execute-api.us-east-1.amazonaws.com/dev"

# 2. Test OpenAPI
print("\nTesting GET /dev/openapi.json...")
req = urllib.request.Request(f"{base_url}/openapi.json")
with urllib.request.urlopen(req, timeout=15) as resp:
    print("OpenAPI Status:", resp.status)
    spec = json.loads(resp.read().decode("utf-8"))
    print("OpenAPI Title:", spec.get("info", {}).get("title"))
    print("Total paths:", len(spec.get("paths", {})))

# 3. Test POST /dev/api/research
print("\nTesting POST /dev/api/research with Cognito JWT...")
payload = json.dumps({
    "system_specification": "Autonomous Drone Quadcopter flight controller with ESC telemetry and power monitor",
    "project_name": "AeroFlight-V1",
    "target_days": 14
}).encode("utf-8")
headers = {
    "Authorization": f"Bearer {id_token}",
    "Content-Type": "application/json"
}
req = urllib.request.Request(f"{base_url}/api/research", data=payload, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("Research API Status:", resp.status)
        data = json.loads(resp.read().decode("utf-8"))
        print("Response keys:", list(data.keys()))
        if "components" in data:
            print("Components count:", len(data["components"]))
        if "project" in data:
            print("Project generated:", data["project"].get("title") or data["project"].get("project_id"))
        print("\nSUCCESS: All AWS components (API Gateway + Cognito Authorizer + Lambda backend) verified working live!")
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.reason)
    print("Response body:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
