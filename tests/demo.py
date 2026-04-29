import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import lognote

def dummy_func(x):
    return x * 2

def test_performance():
    print("Running performance benchmark (100,000 function calls)...")
    
    # Baseline
    start = time.perf_counter()
    for i in range(100000):
        dummy_func(i)
    baseline_time = time.perf_counter() - start
    print(f"Baseline (no tracing): {baseline_time:.4f} seconds")

    # With Lognote
    lognote.ignite()
    start = time.perf_counter()
    for i in range(100000):
        dummy_func(i)
    lognote_time = time.perf_counter() - start
    print(f"With lognote tracing: {lognote_time:.4f} seconds")
    
    overhead = (lognote_time - baseline_time) / 100000
    print(f"Overhead per function call: {overhead * 1e6:.2f} microseconds")
    
    lognote.shutdown()

def faulty_operation(token, cc, ssn):
    divisor = 0
    # The crash happens here
    return 100 / divisor

def crash_simulation():
    print("\nSimulating a crash with sensitive data...")
    lognote.ignite()
    
    secret_token = "sk_live_998877665544332211"
    credit_card = "4111-2222-3333-4444"
    ssn = "123-45-6789"
    
    # This will cause a zero division error and crash the app
    faulty_operation(secret_token, credit_card, ssn)

if __name__ == "__main__":
    test_performance()
    
    # We run crash simulation. Because we use sys.excepthook, the program will terminate with it
    # But for script execution, we don't catch it so sys.excepthook triggers natively.
    crash_simulation()
