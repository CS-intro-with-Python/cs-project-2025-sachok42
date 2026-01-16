import requests
import json
import time

# Base URL for the application
BASE_URL = "http://localhost:5001"

# Test results tracking
tests_passed = 0
tests_failed = 0


def print_test(test_name, passed):
    """Print test result"""
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        print(f"PASS: {test_name}")
    else:
        tests_failed += 1
        print(f"FAIL: {test_name}")


def test_registration_valid():
    """Test user registration with valid data"""
    response = requests.post(f"{BASE_URL}/register", data={
        'username': f'testuser_{int(time.time())}',
        'password': 'testpass123'
    }, allow_redirects=False)

    passed = response.status_code == 302  # Should redirect to login
    print_test("Registration with valid data", passed)


def test_registration_duplicate():
    """Test registration fails with duplicate username"""
    username = f'duplicate_{int(time.time())}'

    # Register first time
    requests.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': 'pass123'
    })

    # Try to register again with same username
    response = requests.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': 'differentpass'
    })

    passed = response.status_code == 400
    print_test("Registration with duplicate username (should fail)", passed)


def test_login_valid():
    """Test login with valid credentials"""
    username = f'loginuser_{int(time.time())}'
    password = 'correctpass'

    # Register user
    requests.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': password
    })

    # Try to login
    response = requests.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': password
    }, allow_redirects=False)

    passed = response.status_code == 302  # Should redirect to home
    print_test("Login with valid credentials", passed)


def test_login_invalid():
    """Test login fails with wrong password"""
    username = f'wrongpass_{int(time.time())}'

    # Register user
    requests.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': 'correctpass'
    })

    # Try wrong password
    response = requests.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': 'wrongpass'
    })

    passed = response.status_code == 401
    print_test("Login with wrong password (should fail)", passed)


def test_access_without_login():
    """Test accessing protected route without login"""
    # Create a new session (not logged in)
    session = requests.Session()
    response = session.get(f"{BASE_URL}/", allow_redirects=False)

    passed = response.status_code == 302 and '/login' in response.headers.get('Location', '')
    print_test("Access protected route without login (should redirect)", passed)


def test_save_diagram_without_auth():
    """Test saving diagram requires authentication"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/save_diagram",
                            json={
                                'name': 'Test Diagram',
                                'diagram': {'name-1': 'Set1'},
                                'thumbnail': ''
                            }
                            )

    passed = response.status_code == 401
    print_test("Save diagram without authentication (should fail)", passed)


def test_save_and_load_diagram():
    """Test complete workflow: register, login, save, load diagram"""
    username = f'workflow_{int(time.time())}'
    password = 'pass123'

    # Create session to maintain cookies
    session = requests.Session()

    # 1. Register
    response = session.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': password
    })

    # 2. Login
    response = session.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': password
    })

    # 3. Save diagram
    diagram_data = {
        'name': 'My Test Diagram',
        'diagram': {
            'name-1': 'Fruits',
            'data-1': 'apple,banana,cherry',
            'name-2': 'Red Things',
            'data-2': 'apple,cherry,strawberry'
        },
        'thumbnail': '<svg>test</svg>'
    }

    response = session.post(f"{BASE_URL}/save_diagram", json=diagram_data)
    save_ok = response.status_code == 200

    # 4. Load thumbnails
    response = session.get(f"{BASE_URL}/load_thumbnails")
    thumbnails = response.json()
    load_ok = len(thumbnails) > 0 and thumbnails[0]['name'] == 'My Test Diagram'

    passed = save_ok and load_ok
    print_test("Complete workflow: register → login → save → load", passed)


def test_load_nonexistent_diagram():
    """Test loading non-existent diagram returns 404"""
    username = f'load404_{int(time.time())}'
    session = requests.Session()

    # Register and login
    session.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': 'pass123'
    })
    session.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': 'pass123'
    })

    # Try to load non-existent diagram
    response = session.get(f"{BASE_URL}/load_diagram/99999")

    passed = response.status_code == 404
    print_test("Load non-existent diagram (should return 404)", passed)


def test_multiple_diagrams():
    """Test saving and loading multiple diagrams"""
    username = f'multi_{int(time.time())}'
    session = requests.Session()

    # Register and login
    session.post(f"{BASE_URL}/register", data={
        'username': username,
        'password': 'pass123'
    })
    session.post(f"{BASE_URL}/login", data={
        'username': username,
        'password': 'pass123'
    })

    # Save 3 diagrams
    for i in range(3):
        session.post(f"{BASE_URL}/save_diagram", json={
            'name': f'Diagram {i + 1}',
            'diagram': {'name-1': f'Set{i}'},
            'thumbnail': ''
        })

    # Load all diagrams
    response = session.get(f"{BASE_URL}/load_thumbnails")
    diagrams = response.json()

    passed = len(diagrams) == 3
    print_test("Save and load multiple diagrams", passed)


def test_user_data_isolation():
    """Test that users cannot see each other's diagrams"""
    user1 = f'isolation1_{int(time.time())}'
    user2 = f'isolation2_{int(time.time())}'

    # User 1 session
    session1 = requests.Session()
    session1.post(f"{BASE_URL}/register", data={'username': user1, 'password': 'pass1'})
    session1.post(f"{BASE_URL}/login", data={'username': user1, 'password': 'pass1'})
    session1.post(f"{BASE_URL}/save_diagram", json={
        'name': 'User1 Private Diagram',
        'diagram': {'name-1': 'Private'},
        'thumbnail': ''
    })

    # User 2 session
    session2 = requests.Session()
    session2.post(f"{BASE_URL}/register", data={'username': user2, 'password': 'pass2'})
    session2.post(f"{BASE_URL}/login", data={'username': user2, 'password': 'pass2'})

    # User 2 should see no diagrams
    response = session2.get(f"{BASE_URL}/load_thumbnails")
    diagrams = response.json()

    passed = len(diagrams) == 0
    print_test("User data isolation (users can't see each other's diagrams)", passed)


def test_delete_diagram():
    """Test deleting a diagram"""
    username = f'delete_{int(time.time())}'
    session = requests.Session()

    # Register, login, save
    session.post(f"{BASE_URL}/register", data={'username': username, 'password': 'pass123'})
    session.post(f"{BASE_URL}/login", data={'username': username, 'password': 'pass123'})
    session.post(f"{BASE_URL}/save_diagram", json={
        'name': 'To Be Deleted',
        'diagram': {'name-1': 'Test'},
        'thumbnail': ''
    })

    # Get diagram ID
    response = session.get(f"{BASE_URL}/load_thumbnails")
    diagrams = response.json()
    diagram_id = diagrams[0]['id']

    # Delete it
    response = session.delete(f"{BASE_URL}/delete_diagram/{diagram_id}")
    delete_ok = response.status_code == 200

    # Verify it's gone
    response = session.get(f"{BASE_URL}/load_thumbnails")
    diagrams = response.json()
    verify_ok = len(diagrams) == 0

    passed = delete_ok and verify_ok
    print_test("Delete diagram", passed)


def test_logout():
    """Test logout clears session"""
    username = f'logout_{int(time.time())}'
    session = requests.Session()

    # Register and login
    session.post(f"{BASE_URL}/register", data={'username': username, 'password': 'pass123'})
    session.post(f"{BASE_URL}/login", data={'username': username, 'password': 'pass123'})

    # Verify authenticated (can access home page)
    response = session.get(f"{BASE_URL}/", allow_redirects=False)
    auth_ok = response.status_code == 200

    # Logout
    session.get(f"{BASE_URL}/logout")

    # Verify not authenticated anymore
    response = session.get(f"{BASE_URL}/", allow_redirects=False)
    logout_ok = response.status_code == 302 and '/login' in response.headers.get('Location', '')

    passed = auth_ok and logout_ok
    print_test("Logout clears session", passed)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RUNNING EULER DIAGRAM VISUALIZER TESTS")
    print("=" * 60)
    print(f"Testing application at: {BASE_URL}")
    print()

    # Check if app is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("ERROR: Application is not running!")
        print(f"Please start the app first: python app.py")
        return

    print("Running Input Validation Tests...")
    test_registration_valid()
    test_registration_duplicate()
    test_login_valid()
    test_login_invalid()
    print()

    print("Running Error Handling Tests...")
    test_access_without_login()
    test_save_diagram_without_auth()
    test_load_nonexistent_diagram()
    print()

    print("Running Integration Tests...")
    test_save_and_load_diagram()
    test_multiple_diagrams()
    test_user_data_isolation()
    test_delete_diagram()
    test_logout()
    print()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")

    if tests_failed == 0:
        print()
        print("ALL TESTS PASSED!")
    else:
        print()
        print(f"{tests_failed} test(s) failed. Please review.")

    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()