import requests
import json
import uuid

BASE_URL = "http://localhost:8000" # Internal container port

def test_api():
    # 1. Register User
    print("Testing User Registration...")
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    reg_payload = {
        "email": email,
        "full_name": "API Test User",
        "clearance_level": 1
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
    user_id = resp.json()["data"]["user_id"]
    print(f"SUCCESS: Created user {user_id}")

    # 2. Login to get token
    print("\nTesting Login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Logged in")

    # 3. Create Case (to associate insight)
    print("\nTesting Case Creation...")
    case_resp = requests.post(f"{BASE_URL}/cases/", json={"title": "API Verification Case", "status": "active"}, headers=headers)
    case_id = case_resp.json()["case_id"]
    print(f"SUCCESS: Created case {case_id}")

    # 4. Create Ingest Job (Primary Data Entry)
    print("\nTesting Ingest Upload API...")
    # Note: Using multipart/form-data for /upload
    files = [
        ('files', ('test.txt', 'test content', 'text/plain'))
    ]
    data = {
        "case_id": str(case_id),
        "source_type": "automated_verification"
    }
    resp = requests.post(f"{BASE_URL}/ingest/upload", files=files, data=data, headers=headers)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
    else:
        job_id = resp.json()["job_id"]
        print(f"SUCCESS: Created ingest job {job_id}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    test_api()
