# 🛡️ Enterprise LLM CI/CD Regression & Evaluation Harness

[![CI Evaluation Pipeline](https://github.com/jayeshaswani67/forward-deployed-eval-harness/actions/workflows/llm_eval.yml/badge.svg)](https://github.com/jayeshaswani67/forward-deployed-eval-harness/actions)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> An enterprise-grade pre-merge testing and regression gatekeeper for LLM applications. Automatically evaluates faithfulness, grounding, latency budgets, and adversarial injection resistance before changes reach production prompts or RAG retrieval pipelines.

---

## 📌 Executive Summary & Architecture

Uncontrolled modifications to system prompts, context chunking strategies, or retrieval pipelines frequently lead to silent hallucinations, format deviations, or latency regressions in production LLM applications.

This repository implements a **Two-Tier CI/CD Quality Gate**:
1. **Deterministic Fast Verification:** Zero-cost schema validation, forbidden token and credential leak scanning, keyword compliance, and latency tracking.
2. **LLM-as-a-Judge Evaluation:** Semantic scoring against a versioned Golden Dataset to assess context grounding, faithfulness, and prompt-injection resilience.

```text
[ Pull Request Created / Modified ]
                 │
                 ▼
     [ GitHub Actions CI Runner ]
                 │
        ┌────────┴────────┐
        ▼                 ▼
 [ Tier 1: Deterministic ] [ Tier 2: LLM Judge Harness ]
  • Pydantic Schema Check   • Golden Dataset Benchmark
  • Secret Leak Scanning    • Semantic Faithfulness Judge
  • Latency Budget (≤3.5s)  • Prompt Injection Resistance
        └────────┬────────┘
                 │
                 ▼
     [ Quality Threshold Gate ]
     ├── Passes All Checks ──► Post PR Comment ──► Allow Merge
     └── Fails Thresholds  ──► Block PR (Exit 1) ──► Post Regression Diff
```

---

## 🎯 Quality Gates & Hard Thresholds

Any Pull Request that breaches these thresholds immediately fails the CI pipeline:

| Metric | Target | Description |
| :--- | :---: | :--- |
| **Faithfulness Score** | `≥ 85.0%` | LLM-as-a-judge score verifying output is strictly grounded in context snippets. |
| **Schema Compliance** | `100.0%` | Ensures all output structures conform to deterministic Pydantic specifications. |
| **Keyword / Guardrail Adherence** | `≥ 90.0%` | Mandatory presence of required SLA clauses and absence of leaked credentials or VPC data. |
| **Mean Execution Latency** | `≤ 3.50s` | Ensures changes to prompts or tool bindings do not violate end-user SLA limits. |

---


---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Google Gemini API Key or OpenAI API Key

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/jayeshaswani67/forward-deployed-eval-harness.git
cd forward-deployed-eval-harness

# Create and activate virtual environment
python -m venv .venv

# Windows (Command Prompt)
.venv\Scripts\activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Running Tests & Benchmarks

### 1. Zero-Cost Unit Tests (Pytest)
Runs local unit tests with mocked API clients to verify fallbacks without token consumption:
```bash
pytest -v
```

### 2. End-to-End Evaluation Pipeline
Runs the benchmark against `golden_cases.json`, writes `eval_results.json`, and enforces quality thresholds:
```bash
python eval/run_evals.py
```

### 3. Generate Pull Request Markdown Summary
Outputs the formatted evaluation table posted to GitHub PRs:
```bash
python eval/format_pr_comment.py
```

---

## 📊 Real-Time Observability Dashboard

The project includes an integrated dark-mode observability dashboard powered by **Chart.js** and Tailwind CSS.

Start the dashboard locally:
```bash
python app/ui.py
```

Open your browser at `http://127.0.0.1:8085` to view:
- **Quality Gate Radar:** Multi-axis capability visualization (Faithfulness, Schema, Latency Margin, Gate Ratios).
- **Latency Distribution vs. Budget:** Per-case execution latency plotted against the $3.5\text{s}$ SLA threshold.
- **Faithfulness Stratification:** Passing vs. Marginal vs. Failing response distribution.
- **Interactive Suite Execution:** Trigger evaluation runs directly from the browser UI.

---

## 🤖 GitHub Actions CI/CD Integration

To run automated checks on every pull request:
1. Navigate to your repository on GitHub.
2. Go to **Settings > Secrets and variables > Actions**.
3. Create a **New repository secret**:
   - **Name:** `GEMINI_API_KEY`
   - **Secret:** Paste your API key.

When a Pull Request modifies files in `app/**`, `prompts/**`, or `eval/**`, GitHub Actions automatically runs the suite, posts the evaluation breakdown as a PR comment, and blocks merging if any threshold fails.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.