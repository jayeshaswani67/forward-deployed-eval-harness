# Enterprise LLM CI/CD Regression & Evaluation Harness

An automated evaluation and pre-merge regression testing pipeline designed to prevent model hallucinations, schema breakages, and latency regressions in production LLM applications.

---

## 🎯 Who It Is For

This framework is built specifically for:

* **Forward Deployed Engineers (FDEs):** Deploying client-facing AI systems into sensitive enterprise environments where silent model drift or bad prompt edits cannot be tolerated.
* **AI/ML Platform & Software Engineers:** Managing production RAG pipelines, autonomous agents, or LLM-backed services who need automated CI quality gates instead of manual spot-checking.
* **Technical Product Teams:** Requiring transparent verification metrics (faithfulness scores, schema validation, and latency tracking) before merging PRs or promoting models to production.

---

## 💡 What It Does

The harness acts as a strict automated gatekeeper between code/prompt revisions and production deployment:

* **Automated CI/CD Quality Gates:** Runs as a GitHub Actions workflow on every pull request touching agent logic, context retrieval, or prompt templates.
* **Deterministic Boundary Verification:** Tests non-negotiable enterprise constraints (strict JSON schema compliance, keyword inclusion, PII/forbidden token leaks) with zero token cost.
* **Semantic LLM-as-a-Judge Evaluation:** Uses an impartial evaluation model to grade generated outputs against a versioned Golden Dataset, scoring semantic faithfulness and prompt-injection resilience.
* **Latency Budget Enforcement:** Monitors round-trip execution latency per test case, blocking pull requests that breach predefined SLA budgets (e.g., $\le 3.5\text{s}$).
* **PR Feedback & Visual Telemetry:** Automatically posts an executive markdown summary directly to the Pull Request and serves a real-time browser dashboard displaying evaluation radars, latency distributions, and test stratifications.

---

## 🏗️ Architecture & Workflow

The pipeline utilizes a two-tier verification approach to keep CI fast, reliable, and cost-effective:

```
               [ Pull Request Created / Updated ]
                               │
                               ▼
                   [ GitHub Actions Runner ]
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
 [ Tier 1: Deterministic Engine ]       [ Tier 2: Semantic Judge ]
  • Regex & Keyword Matching             • LLM-as-a-Judge Scorer
  • Pydantic Schema Validation           • Context Grounding & Faithfulness
  • Secret & Credential Leak Checks      • Adversarial Injection Defense
  • Latency Budget Verification          • Edge-case Benchmark Dataset
         └─────────────────────┬─────────────────────┘
                               │
                               ▼
                 [ Composite Gate Evaluation ]
                               │
           ┌───────────────────┴───────────────────┐
           ▼                                       ▼
     [ All Passed ]                         [ Any Breach ]
  • Exit Code: 0                         • Exit Code: 1
  • Post PR Summary Table                • Post Blocking Annotation & Diff
  • Merge Allowed                        • PR Blocked Until Fixed
```

---

## 🧩 Core Components

1. **Retrieval Agent (`app/agent.py`):** The target system under test. Wraps LLM interactions with structured Pydantic response formatting, telemetry metrics (tokens, latency), and resilient fallback logic.
2. **Deterministic Evaluators (`eval/evaluators/deterministic.py`):** High-speed, local verification utilities that check output schema adherence, presence of mandatory business terms, and absence of sensitive system tokens.
3. **Semantic LLM Judge (`eval/evaluators/llm_judge.py`):** An automated evaluator that prompts a frontier model to grade whether the agent's answer is strictly grounded in the provided reference context.
4. **Golden Dataset (`eval/dataset/golden_cases.json`):** A curated test suite containing standard queries, multi-document retrieval edge cases, and adversarial prompt-injection payloads.
5. **Quality Gate Runner (`eval/run_evals.py`):** The orchestration engine that executes the benchmark suite, evaluates composite metrics against hard target thresholds, and sets the CI process exit code.
6. **Observability Dashboard (`app/ui.py`):** A lightweight server rendering telemetry visualizers (quality radars, SLA latency comparisons, and test case distributions).

---

## 🚦 Quality Gate Thresholds

Pull requests are automatically evaluated against the following standards:

| Metric | Target | Description |
| :--- | :---: | :--- |
| **Faithfulness Score** | $\ge 85.0\%$ | Semantic judge verification that statements derive from source context. |
| **Schema Compliance** | $100.0\%$ | Validates structural fields against Pydantic models. |
| **Keyword Adherence** | $\ge 90.0\%$ | Checks mandatory service terms and enforces zero forbidden leaks. |
| **Average Latency** | $\le 3.50\text{s}$ | Maximum allowable average end-to-end response latency. |
