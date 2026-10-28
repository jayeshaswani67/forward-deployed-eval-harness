import http.server
import socketserver
import socket
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LLM Eval Observability & Regression Suite</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { background-color: #0b0d13; color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .glass-card { background: rgba(17, 21, 33, 0.75); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.07); }
    .glass-card:hover { border-color: rgba(255, 255, 255, 0.14); }
  </style>
</head>
<body class="min-h-screen p-6 lg:p-10 flex flex-col items-center">
  <div class="w-full max-w-6xl space-y-6">
    
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
      <div>
        <div class="flex items-center gap-3">
          <span class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <h1 class="text-xl md:text-2xl font-semibold tracking-tight text-white">LLM CI/CD Regression Observatory</h1>
          <span class="px-2 py-0.5 text-xs font-mono bg-zinc-800 text-zinc-400 rounded border border-white/10">v2.0-telemetry</span>
        </div>
        <p class="text-xs text-zinc-400 mt-1">Automated evaluation gates: faithfulness, structural adherence, latency budgets, and adversarial safety.</p>
      </div>
      <div class="flex items-center gap-3">
        <button id="runBtn" onclick="runEval()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-950">
          <svg id="spinner" class="animate-spin h-4 w-4 hidden" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span id="btnText">Trigger CI Suite</span>
        </button>
      </div>
    </header>

    <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="glass-card p-4 rounded-xl flex flex-col justify-between">
        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Mean Faithfulness</span>
        <div class="text-2xl font-mono font-semibold text-white mt-1" id="m-faith">--%</div>
        <div class="w-full bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div id="bar-faith" class="bg-emerald-500 h-full transition-all duration-500" style="width: 0%"></div>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl flex flex-col justify-between">
        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Schema Compliance</span>
        <div class="text-2xl font-mono font-semibold text-white mt-1" id="m-schema">--%</div>
        <div class="w-full bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div id="bar-schema" class="bg-indigo-500 h-full transition-all duration-500" style="width: 0%"></div>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl flex flex-col justify-between">
        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Keyword Adherence</span>
        <div class="text-2xl font-mono font-semibold text-white mt-1" id="m-keywords">--%</div>
        <div class="w-full bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div id="bar-keywords" class="bg-cyan-500 h-full transition-all duration-500" style="width: 0%"></div>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl flex flex-col justify-between">
        <span class="text-xs font-medium uppercase tracking-wider text-zinc-400">Mean Latency</span>
        <div class="text-2xl font-mono font-semibold text-white mt-1" id="m-latency">--s</div>
        <div class="w-full bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div id="bar-latency" class="bg-amber-500 h-full transition-all duration-500" style="width: 0%"></div>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="glass-card p-4 rounded-xl flex flex-col">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Quality Gate Radar</span>
        <div class="relative flex-1 min-h-[240px]">
          <canvas id="radarChart"></canvas>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl flex flex-col">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Case Latency vs. Budget (3.5s)</span>
        <div class="relative flex-1 min-h-[240px]">
          <canvas id="latencyChart"></canvas>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl flex flex-col">
        <span class="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Faithfulness Stratification</span>
        <div class="relative flex-1 min-h-[240px] flex items-center justify-center">
          <canvas id="donutChart"></canvas>
        </div>
      </div>
    </section>

    <div id="gate-banner" class="hidden p-4 rounded-xl border text-sm font-medium flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span id="gate-icon" class="text-lg"></span>
        <span id="gate-message"></span>
      </div>
      <span class="text-xs font-mono text-zinc-400">Gate Verification: <span id="gate-code">PASS</span></span>
    </div>

    <section class="glass-card rounded-xl overflow-hidden">
      <div class="p-4 border-b border-white/5 flex items-center justify-between">
        <h2 class="text-xs font-semibold text-zinc-300 uppercase tracking-wider">Granular Test Breakdown</h2>
        <span id="case-count" class="text-xs text-zinc-500 font-mono">0 cases tracked</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-zinc-300">
          <thead class="bg-white/[0.02] text-xs font-medium text-zinc-400 uppercase tracking-wider border-b border-white/5 font-mono">
            <tr>
              <th class="py-3 px-4">Case ID</th>
              <th class="py-3 px-4">Faithfulness</th>
              <th class="py-3 px-4">Keywords</th>
              <th class="py-3 px-4">Latency</th>
              <th class="py-3 px-4">Schema</th>
              <th class="py-3 px-4">Evaluator Assessment</th>
            </tr>
          </thead>
          <tbody id="cases-tbody" class="divide-y divide-white/5 font-mono text-xs">
            <tr>
              <td colspan="6" class="py-8 text-center text-zinc-500">Awaiting benchmark results...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
    let radarInstance = null;
    let latencyInstance = null;
    let donutInstance = null;

    async function loadData() {
      try {
        const res = await fetch('/api/results');
        if (!res.ok) return;
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error("Failed to load results:", err);
      }
    }

    function renderDashboard(data) {
      if (!data || !data.metrics) return;
      const m = data.metrics;
      const details = data.details || [];

      document.getElementById('m-faith').innerText = (m.avg_faithfulness * 100).toFixed(1) + '%';
      document.getElementById('m-schema').innerText = (m.schema_pass_rate * 100).toFixed(0) + '%';
      document.getElementById('m-keywords').innerText = (m.avg_keywords * 100).toFixed(1) + '%';
      document.getElementById('m-latency').innerText = m.avg_latency.toFixed(2) + 's';

      document.getElementById('bar-faith').style.width = `${Math.min(100, m.avg_faithfulness * 100)}%`;
      document.getElementById('bar-schema').style.width = `${Math.min(100, m.schema_pass_rate * 100)}%`;
      document.getElementById('bar-keywords').style.width = `${Math.min(100, m.avg_keywords * 100)}%`;
      document.getElementById('bar-latency').style.width = `${Math.min(100, (m.avg_latency / 3.5) * 100)}%`;

      const passed = m.avg_faithfulness >= 0.85 && m.schema_pass_rate === 1.0 && m.avg_keywords >= 0.90 && m.avg_latency <= 3.5;
      const banner = document.getElementById('gate-banner');
      banner.className = `p-4 rounded-xl border text-sm font-medium flex items-center justify-between ${
        passed ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
      }`;
      document.getElementById('gate-icon').innerText = passed ? '✅' : '❌';
      document.getElementById('gate-message').innerText = passed 
        ? 'All deployment regression thresholds satisfied. Ready for merge.' 
        : 'Regression gate triggered. Deployment blocked.';
      document.getElementById('gate-code').innerText = passed ? '0 (CLEARED)' : '1 (BLOCKED)';
      banner.classList.remove('hidden');

      const tbody = document.getElementById('cases-tbody');
      tbody.innerHTML = '';
      document.getElementById('case-count').innerText = `${details.length} cases tracked`;

      details.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-white/[0.02] transition-colors';
        tr.innerHTML = `
          <td class="py-3 px-4 text-white font-semibold">${row.id}</td>
          <td class="py-3 px-4 ${row.faithfulness >= 0.85 ? 'text-emerald-400' : 'text-rose-400'}">${(row.faithfulness * 100).toFixed(0)}%</td>
          <td class="py-3 px-4 ${(row.keyword_score || 0) >= 0.9 ? 'text-emerald-400' : 'text-rose-400'}">${((row.keyword_score || 0) * 100).toFixed(0)}%</td>
          <td class="py-3 px-4 text-zinc-400">${row.latency.toFixed(2)}s</td>
          <td class="py-3 px-4">${row.schema_pass ? '✅ Valid' : '❌ Failed'}</td>
          <td class="py-3 px-4 text-zinc-400 font-sans max-w-xs truncate" title="${row.reason}">${row.reason || 'N/A'}</td>
        `;
        tbody.appendChild(tr);
      });

      renderCharts(m, details);
    }

    function renderCharts(m, details) {
      const radarCtx = document.getElementById('radarChart').getContext('2d');
      if (radarInstance) radarInstance.destroy();
      
      const latencyEfficiency = Math.max(0, 1 - (m.avg_latency / 3.5));

      radarInstance = new Chart(radarCtx, {
        type: 'radar',
        data: {
          labels: ['Faithfulness', 'Schema', 'Keywords', 'Latency Margin', 'Gate Ratio'],
          datasets: [
            {
              label: 'Active Run',
              data: [m.avg_faithfulness, m.schema_pass_rate, m.avg_keywords, latencyEfficiency, m.avg_faithfulness >= 0.85 ? 1 : 0.4],
              backgroundColor: 'rgba(99, 102, 241, 0.25)',
              borderColor: '#6366f1',
              borderWidth: 2,
              pointBackgroundColor: '#6366f1'
            },
            {
              label: 'Threshold Gate',
              data: [0.85, 1.0, 0.90, 0.5, 1.0],
              borderColor: 'rgba(239, 68, 68, 0.6)',
              borderWidth: 1.5,
              borderDash: [4, 4],
              fill: false,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              min: 0,
              max: 1,
              ticks: { display: false, stepSize: 0.2 },
              grid: { color: 'rgba(255, 255, 255, 0.08)' },
              angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
              pointLabels: { color: '#9ca3af', font: { size: 10 } }
            }
          },
          plugins: { legend: { display: true, position: 'bottom', labels: { boxWidth: 10, color: '#9ca3af', font: { size: 10 } } } }
        }
      });

      const latencyCtx = document.getElementById('latencyChart').getContext('2d');
      if (latencyInstance) latencyInstance.destroy();

      const labels = details.map(d => d.id);
      const latencies = details.map(d => d.latency);

      latencyInstance = new Chart(latencyCtx, {
        type: 'bar',
        data: {
          labels: labels.length ? labels : ['tc_001', 'tc_002'],
          datasets: [{
            label: 'Latency (s)',
            data: latencies.length ? latencies : [0, 0],
            backgroundColor: latencies.map(l => l <= 3.5 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(244, 63, 94, 0.7)'),
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: Math.max(4.0, ...latencies) + 0.5,
              grid: { color: 'rgba(255, 255, 255, 0.06)' },
              ticks: { color: '#9ca3af', font: { size: 10 } }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#9ca3af', font: { size: 10 } }
            }
          },
          plugins: { legend: { display: false } }
        }
      });

      const donutCtx = document.getElementById('donutChart').getContext('2d');
      if (donutInstance) donutInstance.destroy();

      let passing = 0, marginal = 0, failing = 0;
      details.forEach(d => {
        if (d.faithfulness >= 0.85) passing++;
        else if (d.faithfulness >= 0.5) marginal++;
        else failing++;
      });

      donutInstance = new Chart(donutCtx, {
        type: 'doughnut',
        data: {
          labels: ['Passed (≥85%)', 'Marginal (50-84%)', 'Failed (<50%)'],
          datasets: [{
            data: details.length ? [passing, marginal, failing] : [1, 0, 0],
            backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
            borderColor: '#0b0d13',
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 10, color: '#9ca3af', font: { size: 10 } } }
          }
        }
      });
    }

    async function runEval() {
      const btn = document.getElementById('runBtn');
      const btnText = document.getElementById('btnText');
      const spinner = document.getElementById('spinner');

      btn.disabled = true;
      btn.classList.add('opacity-60');
      spinner.classList.remove('hidden');
      btnText.innerText = 'Benchmarking...';

      try {
        await fetch('/api/run', { method: 'POST' });
        await loadData();
      } catch (err) {
        alert('CI trigger error: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-60');
        spinner.classList.add('hidden');
        btnText.innerText = 'Trigger CI Suite';
      }
    }

    window.onload = loadData;
  </script>
</body>
</html>
"""

class EvalDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/results":
            results_path = PROJECT_ROOT / "eval_results.json"
            if results_path.exists():
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                with open(results_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/run":
            run_script = PROJECT_ROOT / "eval" / "run_evals.py"
            subprocess.run([sys.executable, str(run_script)], capture_output=True, text=True)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "completed"}')
        else:
            self.send_response(404)
            self.end_headers()


def get_available_port(starting_port=8085):
    """Finds an open port starting from starting_port."""
    port = starting_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return starting_port


if __name__ == "__main__":
    try:
        chosen_port = get_available_port(8085)
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("127.0.0.1", chosen_port), EvalDashboardHandler) as httpd:
            print(f"\n=======================================================", flush=True)
            print(f"🚀 Observability Dashboard running!", flush=True)
            print(f"👉 Open in browser: http://127.0.0.1:{chosen_port}", flush=True)
            print(f"=======================================================\n", flush=True)
            httpd.serve_forever()
    except Exception as exc:
        print(f"FATAL STARTUP ERROR: {exc}", flush=True)
        import traceback
        traceback.print_exc()