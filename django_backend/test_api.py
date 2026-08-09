"""
Test script for verifying Django REST API Auth Gate & Multi-User Data Isolation.
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from api.models import ResearchTask, BenchmarkResult


def test_django_api_isolation():
    print("[TEST] Running Django Auth Gate & User Isolation Tests...\n")
    client = APIClient()

    # 1. Unauthenticated Requests Should Be Blocked (401 Unauthorized)
    print("1. Testing Unauthenticated Access Restrictions...")
    unauth_resp = client.get('/api/v1/research/history/')
    assert unauth_resp.status_code == 401, f"Expected 401 for unauthenticated history request, got {unauth_resp.status_code}"
    print("   [PASS] Unauthenticated access properly blocked (401 Unauthorized).")

    # 2. Register & Login User A
    print("2. Registering and Authenticating User A ('user_a')...")
    client.post('/api/v1/auth/register/', {
        "username": "user_a",
        "email": "user_a@example.com",
        "password": "PasswordA123!"
    }, format='json')

    login_a = client.post('/api/v1/auth/login/', {
        "username": "user_a",
        "password": "PasswordA123!"
    }, format='json')
    token_a = login_a.data.get('token')
    print("   [PASS] User A Token:", token_a[:10] + "...")

    # 3. Create Task for User A directly
    user_a_obj = User.objects.get(username="user_a")
    ResearchTask.objects.create(
        user=user_a_obj,
        topic="User A Private Quantum Computing Research",
        status="COMPLETED",
        final_report="User A report content"
    )

    # 4. Register & Login User B
    print("3. Registering and Authenticating User B ('user_b')...")
    client.post('/api/v1/auth/register/', {
        "username": "user_b",
        "email": "user_b@example.com",
        "password": "PasswordB123!"
    }, format='json')

    login_b = client.post('/api/v1/auth/login/', {
        "username": "user_b",
        "password": "PasswordB123!"
    }, format='json')
    token_b = login_b.data.get('token')
    print("   [PASS] User B Token:", token_b[:10] + "...")

    # 5. Verify User B History DOES NOT include User A's task (Strict User Isolation)
    print("4. Verifying Strict Multi-User Data Isolation...")
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_b)
    history_b = client.get('/api/v1/research/history/')
    assert history_b.status_code == 200, "User B history request failed"
    b_tasks = history_b.data
    print(f"   User B Tasks Count: {len(b_tasks)}")
    assert len(b_tasks) == 0, "Security Failure: User B saw User A's private task!"

    # Verify User A history returns User A's task
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_a)
    history_a = client.get('/api/v1/research/history/')
    assert len(history_a.data) == 1, "User A failed to see their own task"
    print("   [PASS] User A sees 1 task, User B sees 0 tasks. Multi-User Isolation Confirmed!")

    # 6. Verify User Profile Stats
    print("5. Verifying User Profile Endpoint (/api/v1/auth/me/)...")
    me_a = client.get('/api/v1/auth/me/')
    assert me_a.status_code == 200
    assert me_a.data['stats']['total_research_tasks'] == 1
    print("   [PASS] User Profile & Stats verified:", me_a.data['stats'])

    print("\n[SUCCESS] ALL DJANGO AUTH & ISOLATION TESTS PASSED SUCCESSFULLY!")


if __name__ == '__main__':
    test_django_api_isolation()
