import sys
import os
import time
import queue
import threading
import json
import re
from datetime import datetime
from typing import Any, Dict, Optional, Callable
import traceback

class SensitiveFilter:
    def __init__(self):
        self.secret_keys = re.compile(r'(pass|key|token|secret)', re.IGNORECASE)
        self.cc_regex = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        self.ssn_regex = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.ai_hook: Optional[Callable[[str], str]] = None

    def redact(self, data: Any) -> Any:
        if isinstance(data, dict):
            redacted_dict = {}
            for k, v in data.items():
                if self.secret_keys.search(str(k)):
                    redacted_dict[k] = "[REDACTED]"
                else:
                    redacted_dict[k] = self.redact(v)
            return redacted_dict
        elif isinstance(data, (list, tuple)):
            return [self.redact(item) for item in data]
        elif isinstance(data, str):
            # Pattern matching
            val = self.cc_regex.sub("[REDACTED_CC]", data)
            val = self.ssn_regex.sub("[REDACTED_SSN]", val)
            
            # AI Hook (Layer 3)
            if self.ai_hook:
                try:
                    val = self.ai_hook(val)
                except Exception:
                    pass
            return val
        return data

def safe_serialize(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple, set)):
        return [safe_serialize(v) for v in data]
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    else:
        # Prevent huge object representations
        s = str(data)
        if len(s) > 1000:
            return s[:1000] + "..."
        return s

class BackgroundWorker:
    def __init__(self):
        self.queue: queue.Queue = queue.Queue(maxsize=10000)
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.events = []
        self.dropped_events = 0
        self.filter = SensitiveFilter()
        self.session_start = datetime.now().isoformat()
        
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True, name="LognoteWorker")
        self.thread.start()
        
    def stop(self):
        if not self.running:
            return
        self.running = False
        self.queue.put(None)  # Sentinel value
        if self.thread:
            self.thread.join(timeout=2.0)
            
    def enqueue(self, event: Dict[str, Any]):
        if not self.running:
            return
        try:
            self.queue.put_nowait(event)
        except queue.Full:
            self.dropped_events += 1
            
    def _run(self):
        while self.running or not self.queue.empty():
            try:
                event = self.queue.get(timeout=0.1)
                if event is None:
                    break
                
                # Filter and serialize
                filtered_event = self.filter.redact(event)
                safe_event = safe_serialize(filtered_event)
                self.events.append(safe_event)
                
            except queue.Empty:
                continue
            except Exception:
                pass
                
    def flush(self, crash_info: Optional[Dict[str, Any]] = None):
        """Write current events to disk."""
        output = {
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat(),
            "dropped_events": self.dropped_events,
            "events": self.events
        }
        if crash_info:
            output["crash"] = safe_serialize(self.filter.redact(crash_info))
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lognote_trace_{timestamp}.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            print(f"\n[lognote] Trace saved to {filename}")
            
            # Clear events after flush so they don't leak into subsequent sessions
            self.events.clear()
            self.dropped_events = 0
            self.session_start = datetime.now().isoformat()
        except Exception as e:
            print(f"\n[lognote] Failed to save trace: {e}")

# Global worker
_worker = BackgroundWorker()

class Tracer:
    def __init__(self):
        self.project_dir = os.path.abspath(os.getcwd())
        self.active = False
        
        # Site-packages and stdlib filtering optimization
        self.site_packages = [p for p in sys.path if "site-packages" in p or "dist-packages" in p]
        
    def _is_user_code(self, file_path: str) -> bool:
        if not file_path:
            return False
        
        if file_path.startswith("<") and file_path.endswith(">"):
            return False
            
        abs_path = os.path.abspath(file_path)
        if not abs_path.startswith(self.project_dir):
            return False
            
        for sp in self.site_packages:
            if abs_path.startswith(sp):
                return False
                
        return True

    def trace_calls(self, frame, event, arg):
        if event not in ("call", "return", "exception"):
            return self.trace_calls

        code = frame.f_code
        file_path = code.co_filename
        
        # Fast path
        if not self._is_user_code(file_path):
            return None

        # Capture timestamp early
        ts = datetime.now().isoformat()
        
        if event == "call":
            # Extract arguments
            argcount = code.co_argcount
            argnames = code.co_varnames[:argcount]
            locals_dict = frame.f_locals
            inputs = {name: locals_dict.get(name) for name in argnames if name in locals_dict}
            
            _worker.enqueue({
                "type": "call",
                "function": code.co_name,
                "file": file_path,
                "line": frame.f_lineno,
                "timestamp": ts,
                "inputs": inputs
            })
            return self.trace_calls
            
        elif event == "return":
            _worker.enqueue({
                "type": "return",
                "function": code.co_name,
                "file": file_path,
                "line": frame.f_lineno,
                "timestamp": ts,
                "return_value": arg
            })
            
        elif event == "exception":
            exc_type, exc_value, exc_traceback = arg
            _worker.enqueue({
                "type": "exception_caught",
                "function": code.co_name,
                "file": file_path,
                "line": frame.f_lineno,
                "timestamp": ts,
                "exception_type": exc_type.__name__ if exc_type else None,
                "exception_message": str(exc_value)
            })
            
        return self.trace_calls

_tracer = Tracer()
_original_excepthook = sys.excepthook

def _crash_handler(exc_type, exc_value, exc_traceback):
    """Global crash handler to capture unhandled exceptions."""
    print("\n[lognote] Crash detected. Generating flight record...", file=sys.stderr)
    
    # 1. Capture Traceback
    tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_str = "".join(tb_list)
    
    # 2. Capture Variables from the frame where the exception occurred
    tb = exc_traceback
    while tb and tb.tb_next:
        tb = tb.tb_next
    frame = tb.tb_frame if tb else None
    locals_dict = {k: v for k, v in frame.f_locals.items() if not k.startswith('__')} if frame else {}
    
    # 3. Diagnosis (Heuristic / AI Hook)
    diagnosis = f"Unhandled {exc_type.__name__}: {str(exc_value)}. "
    if isinstance(exc_value, KeyError):
        diagnosis += "A dictionary key was accessed that does not exist."
    elif isinstance(exc_value, TypeError):
        diagnosis += "An operation was performed on an incompatible type."
    elif isinstance(exc_value, ValueError):
        diagnosis += "A function received an argument of correct type but inappropriate value."
    elif isinstance(exc_value, AttributeError):
        diagnosis += "An attempt was made to access an attribute that an object does not possess."
    else:
        diagnosis += "[AI Hook] Further diagnosis can be plugged in here via the lognote AI extension."
        
    crash_info = {
        "timestamp": datetime.now().isoformat(),
        "diagnosis": diagnosis,
        "traceback": tb_str,
        "variables": locals_dict,
        "exception_type": exc_type.__name__,
        "exception_message": str(exc_value)
    }
    
    _worker.stop()
    _worker.flush(crash_info=crash_info)
    
    # Call original excepthook
    _original_excepthook(exc_type, exc_value, exc_traceback)


def ignite():
    """Start the flight recorder."""
    _worker.start()
    sys.excepthook = _crash_handler
    sys.settrace(_tracer.trace_calls)

def shutdown():
    """Stop the flight recorder."""
    sys.settrace(None)
    sys.excepthook = _original_excepthook
    _worker.stop()
    _worker.flush()
