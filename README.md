<div align="center">

<!-- Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=lognote&fontSize=80&fontColor=ffffff&fontAlignY=30&desc=The%20AI-Powered%20Flight%20Recorder%20for%20Python&descAlignY=58&descSize=20&descColor=a78bfa" width="100%"/>

<!-- Badges Row 1 -->
<p>
  <img src="https://img.shields.io/pypi/v/lognote?style=for-the-badge&logo=pypi&logoColor=white&color=7c3aed&labelColor=1e1b4b" alt="PyPI Version"/>
  <img src="https://img.shields.io/pypi/pyversions/lognote?style=for-the-badge&logo=python&logoColor=white&color=4f46e5&labelColor=1e1b4b" alt="Python Versions"/>
  <img src="https://img.shields.io/github/license/Nvishal2006/lognote?style=for-the-badge&color=7c3aed&labelColor=1e1b4b" alt="License"/>
  <img src="https://img.shields.io/pypi/dm/lognote?style=for-the-badge&logo=pypi&logoColor=white&color=4f46e5&labelColor=1e1b4b" alt="Downloads"/>
</p>

<!-- Badges Row 2 -->
<p>
  <img src="https://img.shields.io/badge/overhead-%3C%201ms-brightgreen?style=for-the-badge&labelColor=1e1b4b" alt="Overhead"/>
  <img src="https://img.shields.io/badge/config-zero--config-blue?style=for-the-badge&labelColor=1e1b4b" alt="Zero Config"/>
  <img src="https://img.shields.io/badge/privacy-PII%20safe-purple?style=for-the-badge&labelColor=1e1b4b" alt="PII Safe"/>
  <img src="https://img.shields.io/badge/AI-powered-ff6b6b?style=for-the-badge&labelColor=1e1b4b" alt="AI Powered"/>
</p>

<br/>

> **Stop guessing why your production code crashed. Start replaying it.**

<br/>

</div>

---

## 🛩️ What is lognote?

**lognote** acts like an airplane's **Flight Data Recorder** — silently capturing every function call, argument, and variable state in the background. When your app crashes, lognote hands you a full **AI-driven autopsy report** — no print statements, no heavy debuggers, no regrets.

In a world where logs are often **too thin** and debuggers are **too heavy**, lognote sits perfectly in the middle with *Agentic Instrumentation* that works without touching a single line of your existing code.

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                     │
│                                                         │
│   main() → service() → db_query() → 💥 CRASH            |
│      ↑           ↑          ↑                           │
│      └───────────┴──────────┘                           │
│           lognote records EVERYTHING                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 The Real Problem (And How lognote Solves It)

<div align="center">

| 🔴 The Problem | ✅ The lognote Solution |
|:---|:---|
| **The "Heisenbug"** — crashes that vanish under a debugger | Captures the **exact `locals()` state** at the millisecond of failure |
| **Production Latency** — tracing slows everything down | Non-blocking background worker: **main thread overhead < 1ms** |
| **PII Leaks** — passwords & tokens ending up in log files | **Multi-layer Semantic Filter** redacts secrets before they touch disk |
| **Post-Mortem Fatigue** — staring at stack traces for hours | **AI diagnosis** explains *why* the crash happened in plain English |

</div>

---

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                    lognote Flight Recorder                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   Your Code          sys.settrace Engine                         ║ 
║   ──────────  ──►   ─────────────────────                        ║
║   main()             IGNITE: Hook into your project scope        ║
║   service()          FILTER: Skip stdlib & site-packages         ║
║   db_query()         CAPTURE: locals(), args, return values      ║
║                             │                                    ║
║                             ▼                                    ║
║                     ┌───────────────┐                            ║
║                     │  Async Queue  │  ← Non-blocking buffer     ║
║                     └───────┬───────┘                            ║
║                             │                                    ║
║                             ▼                                    ║
║                     ┌───────────────┐                            ║
║                     │ PII Scrubber  │  ← Redacts secrets         ║
║                     └───────┬───────┘                            ║
║                             │                                    ║
║                             ▼                                    ║
║                     ┌───────────────┐                            ║
║                     │  JSON Flight  │  ← Structured record       ║
║                     │    Record     │                            ║
║                     └───────────────┘                            ║
╚══════════════════════════════════════════════════════════════════╝
```

**4 Phases, Zero Effort:**

1. **🔥 Ignite** — `sys.settrace` hooks into every call in your project
2. **🔍 Filter** — Ignores `site-packages` and `stdlib` for maximum performance
3. **📥 Buffer** — Events pushed to a thread-safe `Queue`
4. **💾 Process** — Background thread scrubs PII and writes the `.json` Flight Record

---

## 🚀 Quickstart

### Step 1 — Install

```bash
pip install lognote
```

### Step 2 — One Line. That's It.

```python
import lognote

# 🔥 Ignite the flight recorder
lognote.ignite(output_dir="./traces", secret_scrubbing=True)

# ✅ The rest of your application — completely unchanged
def process_payment(user_id, amount):
    ...

def fetch_user(token):
    ...
```

> No decorators. No wrappers. No config files. Just **one line** at the top of `main.py`.

### Step 3 — Analyze the Crash

When a crash occurs, a `.json` Flight Record is auto-generated. Replay it with the built-in **Time-Travel CLI**:

```bash
python -m lognote view ./traces/lognote_trace_1714412345.json
```

You'll get a beautiful terminal dashboard like this:

```
╔══════════════════════════════════════════════════════════╗
║  🛩  lognote — Flight Record Analysis                    ║
║  File: lognote_trace_1714412345.json                     ║
╠══════════════════════════════════════════════════════════╣
║  Timeline                                                ║
║  ─────────────────────────────────────────────────────── ║
║  14:22:01.001  →  main()         [ENTER]  args={}        ║
║  14:22:01.003  →  fetch_user()   [ENTER]  token=***      ║
║  14:22:01.045  →  db_query()     [ENTER]  sql="SELECT…"  ║
║  14:22:01.099  →  db_query()     [EXIT]   result=None    ║
║  14:22:01.100  →  process()      [ERROR]  💥 CRASH      ║
║                                                          ║
║  🤖 AI Diagnosis                                        ║
║  ─────────────────────────────────────────────────────── ║
║  db_query() returned None because the connection pool    ║
║  was exhausted. process() tried to call .rows on None.   ║
║  Fix: Add a null-check after db_query() or increase      ║
║  MAX_POOL_SIZE in your database config.                  ║
╚══════════════════════════════════════════════════════════╝
```

---

## 💎 Features at a Glance

<div align="center">

| Feature | Description |
|:---|:---|
| 🎯 **Zero-Config** | No decorators, no wrappers. `ignite()` and you're done. |
| 🤖 **Agentic Tracing** | Automatically identifies function boundaries & captures all arguments. |
| 🔒 **Privacy-First** | Built-in RegEx + keyword filters for SSN, passwords, API tokens. |
| ⚡ **Async by Design** | Background worker writes logs — your API latency stays untouched. |
| 🖥️ **Rich Dashboard** | Terminal UI with full event timeline leading to the crash. |
| 🧠 **AI Diagnosis** | Plain-English explanation of *why* the crash happened. |
| 🗂️ **Structured Output** | Portable `.json` flight records — pipe to any observability stack. |

</div>

---

## ⚙️ Configuration Reference

```python
lognote.ignite(
    output_dir    = "./logs",    # Where to save .json flight records
    secret_scrubbing = True,     # Auto-mask: passwords, tokens, SSNs
    max_queue_size   = 1000,     # Cap memory during high-burst execution
)
```

<div align="center">

| Parameter | Default | Description |
|:---|:---:|:---|
| `output_dir` | `./logs` | Directory for `.json` flight records |
| `secret_scrubbing` | `True` | Redact sensitive variable names/values |
| `max_queue_size` | `1000` | Memory ceiling during burst traffic |

</div>

---

## 🔐 Privacy & Security

lognote's **Multi-Layer Semantic Filter** protects your users before data ever reaches disk:

```
Raw Variable State
       │
       ▼
  ┌─────────────────────────────┐
  │  Layer 1: Keyword Match     │  password, token, secret, key, ssn…
  ├─────────────────────────────┤
  │  Layer 2: RegEx Patterns    │  /Bearer [A-Z0-9]+/, credit card…
  ├─────────────────────────────┤
  │  Layer 3: Entropy Scanner   │  High-entropy strings → likely keys
  └─────────────────────────────┘
       │
       ▼
  Scrubbed Record  →  { "token": "***REDACTED***" }
```

---

## 🛣️ Roadmap

- [x] Core `sys.settrace` engine
- [x] Async queue + background worker
- [x] Multi-layer PII scrubber
- [x] Time-Travel CLI viewer
- [x] AI-powered crash diagnosis
- [ ] 🔜 OpenTelemetry export
- [ ] 🔜 Web dashboard (FastAPI + React)
- [ ] 🔜 `async/await` coroutine tracing
- [ ] 🔜 Pytest plugin for trace-on-fail

---

## 🤝 Contributing

lognote is open-source and welcomes contributors! Here's how to get started:

```bash
# Clone the repo
git clone https://github.com/Nvishal2006/lognote.git
cd lognote

# Set up your environment
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/
```

- 🐛 **Found a bug?** [Open an issue on GitHub](https://github.com/Nvishal2006/lognote/issues)
- 💬 **Want to discuss?** [Join the conversation on LinkedIn](https://www.linkedin.com/in/vishal-n2006)
- 🌟 **Like the project?** Star it — it helps more than you'd think!

---

## 👨💻 Author

<div align="center">

<img src="https://img.shields.io/badge/Built%20by-Vishal%20N-7c3aed?style=for-the-badge&logo=github&logoColor=white&labelColor=1e1b4b"/>

**Building tools that make Python production-ready.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vishal-n2006)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nvishal2006)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=100&section=footer" width="100%"/>

**lognote** — *Because every crash deserves a black box.*

<sub>Made with ❤️ by Vishal N · Python Observability · Open Source</sub>

</div>
