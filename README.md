# py-vox - Black Box Flight Recorder

`py-vox` is a high-performance, threading-safe, zero-dependency "Black Box Flight Recorder" for Python applications. Designed specifically for production environments, it captures essential execution paths, performance metrics, and state-at-crash information without slowing down your host application.

## Why py-vox?
When a critical application crashes in production, having an exact playback of what happened is invaluable. However, tracing tools usually require external setups and carry a heavy performance hit or many dependencies.
`py-vox` runs entirely in the Python Standard Library, logging safely inside a lightweight memory buffer (limited to the last 100 events). It strictly monitors for performance bottlenecks and captures local frame variables right before a stack unrolls in severe crashes, meaning no more flying blind. 
Plus, `py-vox` comes with an automatic Privacy Filter, ensuring passwords, tokens, and secret keys never leak into your logs.

## Quick Start

### Installation
Until published on PyPI, you can build it locally:
```bash
pip install .
```

### Usage
```python
from py_vox import trace, monitor, report

# 1. Trace function calls and return values
@trace
def process_payment(user_id: str, secret_token: str, amount: float):
    return {"status": "success", "amount": amount}

# The Privacy Filter will automatically redact "secret_token"
process_payment("u123", "sk_live_123456789", 45.0)

# 2. Monitor code block performance
def heavy_computation():
    with monitor("Data Crunching Task"):
        # Simulated workload
        for i in range(1000000):
            pass

heavy_computation()

# 3. Capture crashes with exact locals
@trace
def faulty_function(my_password: str):
    x = 10
    y = 0
    # On crash, py-vox captures x=10, y=0, and my_password="[REDACTED]"
    return x / y

try:
    faulty_function("my_super_secret_password")
except ZeroDivisionError:
    pass

# 4. Export the session locally
# Generates a JSON (or Markdown) report in the .py_vox_logs directory
report_path = report(format="json")
print(f"Log saved to {report_path}")
```
## Author

**Vishal N** [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vishal-n2006)

Feel free to reach out for collaborations or questions!
