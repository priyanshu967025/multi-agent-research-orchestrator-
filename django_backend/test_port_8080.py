"""
Verification script testing Multi-Agent Research Orchestrator Django server on Port 8080.
"""

import requests

BASE_URL = "http://127.0.0.1:8080/api/v1"

def test_port_8080():
    print("[TEST] Verifying Port 8080 Django API Server Endpoint...")
    
    # 1. Register User on Port 8080
    print("1. Testing Registration on http://127.0.0.1:8080/api/v1/auth/register/...")
    reg_resp = requests.post(f"{BASE_URL}/auth/register/", json={
        "username": "orchestrator_user_8080",
        "email": "user8080@example.com",
        "password": "Password8080!"
    })
    print("   Status Code:", reg_resp.status_code)
    print("   Response Data:", reg_resp.json())
    assert reg_resp.status_code in [201, 400], "Registration on Port 8080 failed"

    # 2. Login User on Port 8080
    print("2. Testing Login on http://127.0.0.1:8080/api/v1/auth/login/...")
    login_resp = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": "orchestrator_user_8080",
        "password": "Password8080!"
    })
    print("   Status Code:", login_resp.status_code)
    print("   Response Data:", login_resp.json())
    assert login_resp.status_code == 200, "Login on Port 8080 failed"
    token = login_resp.json().get("token")
    print("   Auth Token Received:", token[:10] + "...")

    # 3. Test Profile on Port 8080
    print("3. Testing Profile on http://127.0.0.1:8080/api/v1/auth/me/...")
    me_resp = requests.get(f"{BASE_URL}/auth/me/", headers={"Authorization": f"Token {token}"})
    print("   Status Code:", me_resp.status_code)
    print("   Profile Data:", me_resp.json())
    assert me_resp.status_code == 200, "Profile check failed"

    print("\n[SUCCESS] PORT 8080 DJANGO REST API IS 100% OPERATIONAL & VERIFIED!")

if __name__ == '__main__':
    test_port_8080()
