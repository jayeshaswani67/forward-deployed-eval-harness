import json

def generate_markdown():
    try:
        with open("eval_results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("### ⚠️ Evaluation run failed before producing report.")
        return

    m = data["metrics"]
    
    print("## 🤖 CI Evaluation & Regression Gate Results\n")
    print("| Metric | Value | Target | Status |")
    print("| :--- | :--- | :--- | :--- |")
    print(f"| **Faithfulness Score** | {m['avg_faithfulness'] * 100:.1f}% | ≥ 85.0% | {'✅ Pass' if m['avg_faithfulness'] >= 0.85 else '❌ Fail'} |")
    print(f"| **Schema Compliance** | {m['schema_pass_rate'] * 100:.1f}% | 100% | {'✅ Pass' if m['schema_pass_rate'] == 1.0 else '❌ Fail'} |")
    print(f"| **Avg Latency** | {m['avg_latency']:.2f}s | ≤ 3.50s | {'✅ Pass' if m['avg_latency'] <= 3.5 else '❌ Fail'} |\n")
    
    print("<details><summary><b>View Individual Test Case Breakdown</b></summary>\n")
    print("| ID | Faithfulness | Latency | Schema | Reason |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    for row in data["details"]:
        print(f"| `{row['id']}` | {row['faithfulness']:.2f} | {row['latency']:.2f}s | {'✅' if row['schema_pass'] else '❌'} | {row['reason']} |")
    print("\n</details>")

if __name__ == "__main__":
    generate_markdown()