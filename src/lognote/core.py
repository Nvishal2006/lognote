import inspect
import time
import functools
import threading
import json
import re
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Callable, Dict, Literal, Optional
from datetime import datetime

SECRET_KEYS_REGEX = re.compile(r'(pass|key|token|secret)', re.IGNORECASE)

def safe_serialize(data: Any) -> Any:
    """Recursively stringify un-serializable objects so JSON won't crash."""
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return [safe_serialize(v) for v in data]
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        return str(data)

def redact_secrets(data: Any) -> Any:
    """Recursively checks for dictionary keys containing secret-related names and redacts them."""
    if isinstance(data, dict):
        redacted_dict = {}
        for k, v in data.items():
            if SECRET_KEYS_REGEX.search(str(k)):
                redacted_dict[k] = "[REDACTED]"
            else:
                redacted_dict[k] = redact_secrets(v)
        return redacted_dict
    elif isinstance(data, (list, tuple)):
        return [redact_secrets(item) for item in data]
    return data

def format_json(events: list[Dict[str, Any]]) -> str:
    # First, serialize complex objects to strings to prevent JSON errors
    processed_events = [safe_serialize(event) for event in events]
    return json.dumps(processed_events, indent=2)

def format_markdown(events: list[Dict[str, Any]]) -> str:
    lines = ["# lognote Session Log\n"]
    for event in events:
        lines.append(f"## Event: {event.get('type', 'Unknown')} at {event.get('timestamp', 'Unknown')}")
        for k, v in event.items():
            if k not in ('type', 'timestamp'):
                lines.append(f"- **{k}**: {v}")
        lines.append("")
        
    return "\n".join(lines)

class SessionBuffer:
    def __init__(self, maxsize: int = 100):
        self.maxsize = maxsize
        self._buffer: list[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_event(self, event: Dict[str, Any]):
        redacted_event = redact_secrets(event)
        with self._lock:
            self._buffer.append(redacted_event)
            if len(self._buffer) > self.maxsize:
                self._buffer.pop(0)

    def get_events(self) -> list[Dict[str, Any]]:
        with self._lock:
            return list(self._buffer)

# Global session instance
session = SessionBuffer(maxsize=100)

def capture_crash_frame(e: Exception) -> Dict[str, Any]:
    """Uses the inspect module to capture local variable names and values in the current frame."""
    tb = getattr(e, '__traceback__', None)
    if tb is None:
        return {}
    
    # Get the last traceback frame where the error actually occurred before our decorator handling
    while tb.tb_next:
        tb = tb.tb_next
        
    frame = tb.tb_frame
    locals_dict = {k: v for k, v in frame.f_locals.items() if not k.startswith('__')}
    return locals_dict

def trace(func: Callable) -> Callable:
    """A decorator that captures function inputs, execution time, return value and local variables on crash."""
    
    # Pre-compute signature if possible to save time, though it might fail for some C-extensions
    try:
        sig = inspect.signature(func)
    except ValueError:
        sig = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        inputs = {}
        if sig:
            try:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                inputs = dict(bound.arguments)
            except Exception:
                inputs = {"args": args, "kwargs": kwargs}
        else:
            inputs = {"args": args, "kwargs": kwargs}

        event: Dict[str, Any] = {
            "type": "function_call",
            "function": func.__name__,
            "module": func.__module__,
            "timestamp": datetime.now().isoformat(),
            "inputs": inputs
        }
        
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            event["status"] = "success"
            event["return_value"] = result
            event["duration_seconds"] = end_time - start_time
            session.add_event(event)
            return result
        except Exception as e:
            end_time = time.perf_counter()
            event["status"] = "error"
            event["exception"] = str(e)
            event["duration_seconds"] = end_time - start_time
            event["local_vars_at_crash"] = capture_crash_frame(e)
            session.add_event(event)
            raise

    return wrapper

@contextmanager
def monitor(name: str):
    """A context manager to measure execution time of code blocks."""
    start_time = time.perf_counter()
    event: Dict[str, Any] = {
        "type": "block_monitor",
        "name": name,
        "timestamp": datetime.now().isoformat()
    }
    try:
        yield
        end_time = time.perf_counter()
        event["status"] = "success"
        event["duration_seconds"] = end_time - start_time
        session.add_event(event)
    except Exception as e:
        end_time = time.perf_counter()
        event["status"] = "error"
        event["exception"] = str(e)
        event["duration_seconds"] = end_time - start_time
        event["local_vars_at_crash"] = capture_crash_frame(e)
        session.add_event(event)
        raise

def report(format: Literal['json', 'markdown'] = 'json', output_dir: str = '.lognote_logs') -> str:
    """Export the current session buffer into a clean, human-readable file."""
    events = session.get_events()
    dir_path = Path(output_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'markdown':
        content = format_markdown(events)
        file_path = dir_path / f"lognote_report_{timestamp}.md"
    else:
        content = format_json(events)
        file_path = dir_path / f"lognote_report_{timestamp}.json"
        
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)
