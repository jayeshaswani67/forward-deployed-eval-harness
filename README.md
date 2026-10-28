Enterprise LLM CI/CD Regression & Evaluation HarnessAn automated evaluation and pre-merge regression testing pipeline designed to prevent model hallucinations, schema breakages, and latency regressions in production LLM applications.🎯 Who It Is ForThis framework is built specifically for:Forward Deployed Engineers (FDEs) deploying client-facing AI systems into sensitive enterprise environments where silent model drift or bad prompt edits cannot be tolerated.AI/ML Platform & Software Engineers managing production RAG pipelines, agents, or LLM-backed services who need automated CI quality gates instead of manual spot-checking.Technical Product Teams that require transparent verification metrics (faithfulness scores, schema validation, and latency tracking) before merging PRs or promoting models to production.💡 What It DoesThe harness acts as a strict automated gatekeeper between code/prompt revisions and production deployment:Automated CI/CD Quality Gates: Runs as a GitHub Actions workflow on every pull request that touches agent logic, context retrieval, or prompt templates.Deterministic Boundary Verification: Tests non-negotiable enterprise constraints (strict JSON schema compliance, keyword inclusion, PII/forbidden leak detection) with zero token costs.Semantic LLM-as-a-Judge Evaluation: Uses an impartial evaluation model to grade generated outputs against a versioned Golden Dataset, scoring semantic faithfulness and prompt-injection resilience.Latency Budget Enforcement: Monitors round-trip execution latency on a per-case basis, blocking pull requests that breach strict SLA budgets (e.g., $\le 3.5\text{s}$).PR Feedback & Visual Telemetry: Automatically generates and posts an executive markdown summary directly to the Pull Request and serves a real-time browser dashboard displaying evaluation radars, latency distributions, and test stratifications.🏗️ Architecture & WorkflowThe pipeline utilizes a two-tier verification approach to keep CI fast and cost-effective:Plaintext               [ Pull Request Created / Updated ]
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
Core Architecture ComponentsRetrieval Agent (app/agent.py): The target system under test. Wraps LLM interactions with strict Pydantic response formatting, telemetry metrics (tokens, latency), and deterministic fallbacks.Deterministic Evaluators (eval/evaluators/deterministic.py): High-speed, local verification utilities that check output structure, presence of mandatory business terms, and absence of sensitive system tokens.Semantic LLM Judge (eval/evaluators/llm_judge.py): An automated evaluator that prompts a frontier model to grade whether the agent's answer is strictly grounded in the provided reference context.Golden Dataset (eval/dataset/golden_cases.json): A curated test suite containing happy paths, tricky multi-context documents, and adversarial prompt-injection payloads.Quality Gate Runner (eval/run_evals.py): The orchestration engine that executes the test suite, aggregates metrics against hard target thresholds, and sets the CI process exit code.Observability Dashboard (app/ui.py): A lightweight server rendering telemetry visualizers (quality radars, SLA latency comparisons, and test case distributions).