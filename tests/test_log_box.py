import pytest
from log_box.core import trace  # Ensure this matches your actual decorator name

# Test 1: Testing a normal successful function
def test_function_capture():
    @trace
    def dummy_task(token, uid):
        return f"User {uid} verified with {token}"

    # We call the function with values INSIDE the test
    result = dummy_task("secret_123", 42)
    
    assert "verified" in result
    # Add assertions here to check if your log/report captured 'token' and 'uid'

# Test 2: Testing an error and redaction
def test_error_redaction():
    @trace
    def login_attempt(password):
        if password == "12345":
            raise ValueError("Weak password!")
        return True

    # Use pytest.raises to handle the expected crash
    with pytest.raises(ValueError):
        login_attempt("12345")
    
    # Check your logs here to ensure 'password' was changed to '********'