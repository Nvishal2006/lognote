import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import lognote

def faulty_operation(token, cc, ssn):
    divisor = 0
    return 100 / divisor

def process_payment(user_id, amount):
    print(f"Processing payment for {user_id}...")
    time.sleep(0.1)
    secret_token = "sk_live_998877665544332211"
    credit_card = "4111-2222-3333-4444"
    ssn = "123-45-6789"
    
    # This will cause a zero division error and crash the app
    faulty_operation(secret_token, credit_card, ssn)

def crash_simulation():
    print("\nSimulating a crash with sensitive data...")
    lognote.ignite()
    
    process_payment("user_789", 49.99)

if __name__ == "__main__":
    crash_simulation()
