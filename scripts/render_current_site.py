#!/usr/bin/env python3
"""Render the current qualified SparkBench cohort as a compact static page."""

from __future__ import annotations

import argparse
import csv
import html
import re
from datetime import date
from pathlib import Path


MODEL_NAMES = {
    "deepseek-v4-flash": "DeepSeek V4 Flash 0731",
    "qwopus-awq-mtp-k1": "Qwopus AWQ",
    "qwopus-awq": "Qwopus AWQ",
    "aeon-ultimate-mm-control": "Aeon Ultimate MM NVFP4",
    "aeon-ultimate-mm-mtp-k1": "Aeon Ultimate MM NVFP4",
    "gemma4-26b-a4b-q4km": "Gemma 4 26B-A4B Q4_K_M",
    "kat-coder-v2.5-dev-nvfp4": "KAT-Coder V2.5 Dev NVFP4",
    "qwen3.5-9b-mtp-k1": "Qwen 3.5 9B BF16",
    "qwen3.5-9b": "Qwen 3.5 9B BF16",
    "nemotron3-nano-omni-q4km": "Nemotron 3 Nano Omni Q4_K_M",
    "qwen3.6-27b-nvfp4": "Qwen 3.6 27B NVFP4",
    "agents-a1-nvfp4": "Agents A1 NVFP4",
    "qwythos-9b": "Qwythos 9B",
    "qwen3.6-27b-obliteratus-q5km": "Qwen 3.6 27B Obliteratus Q5_K_M",
    "qwen3.6-27b-nvfp4-dflash-k8": "Qwen 3.6 27B NVFP4",
    "qwable-5-27b-coder-q4km": "Qwable 5 27B Coder Q4_K_M",
    "holo-3.1-35b-a3b-q4km": "Holo 3.1 35B-A3B Q4_K_M",
    "huihui-qwen3.6-35b-a3b-q4km": "Huihui Qwen 3.6 35B-A3B Q4_K_M",
    "ornith-1.0-35b-nvfp4": "Ornith 1.0 35B NVFP4",
    "qwen3.6-27b-pitune-q4km": "Qwen 3.6 27B PiTune Q4_K_M",
    "qwen3.6-35b-heretic": "Qwen 3.6 35B Heretic NVFP4",
    "hauhaucs-35b-nvfp4": "HauHauCS 35B NVFP4",
    "nemotron-3-nano-aeon-nvfp4": "Nemotron 3 Nano Aeon NVFP4",
    "qwen3.6-35b-a3b-nvfp4": "Qwen 3.6 35B-A3B NVFP4",
    "deepseek-v4-flash-iq2xxs": "DeepSeek V4 Flash IQ2_XXS",
    "ornith-1.0-35b-dflash-k8": "Ornith 1.0 35B NVFP4",
    "bonsai-27b-q1": "Bonsai 27B Q1",
    "minicpm-v-4.6": "MiniCPM-V 4.6 BF16",
}


def engine_of(label: str) -> str:
    if "-llamacpp-" in label:
        return "llama.cpp"
    if "-DS4-" in label:
        return "DS4"
    return "vLLM"


def context_of(label: str) -> str:
    if "-1M-" in label:
        return "1M"
    if "-65536-" in label or "-65K-" in label:
        return "65K"
    if "-32768-" in label:
        return "32K"
    return "Recorded"


def display_spec(value: str) -> str:
    if value.lower() == "off":
        return "Spec off"
    return value.replace("dflash", "DFlash").replace("dspark", "DSpark")


def score_class(score: float) -> str:
    if score >= 85:
        return "top"
    if score >= 75:
        return "mid"
    return "low"


def render_rows(records: list[dict[str, str]]) -> str:
    rows = []
    cohort_url = (
        "https://github.com/Weschera/spark-bench/tree/main/"
        "results/cohorts/2026-08-01-one-spark-v671/raw"
    )
    for row in records:
        score = float(row["score"])
        label = row["label"]
        model = MODEL_NAMES.get(row["model"], row["model"].replace("-", " ").title())
        engine = engine_of(label)
        context = context_of(label)
        spec = display_spec(row["spec_decode"])
        source_dir = Path(row["csv"]).parent.name
        report = f"{cohort_url}/{source_dir}/runs/{row['run_id']}.html"
        search = html.escape(f"{model} {engine} {spec}".lower(), quote=True)
        rows.append(
            f'''<tr data-engine="{html.escape(engine, quote=True)}" data-search="{search}">
  <td class="rank">{row['rank']}</td>
  <td class="model"><a href="{html.escape(report, quote=True)}">{html.escape(model)}</a>
    <span>{html.escape(engine)} · {html.escape(context)} context · {html.escape(spec)}</span></td>
  <td><strong class="score {score_class(score)}">{score:.1f}</strong><i class="bar"><b style="width:{score:.1f}%"></b></i></td>
  <td>{float(row['quality']):.1f}</td>
  <td>{float(row['calibration']):.1f}</td>
  <td>{float(row['reliability']):.1f}</td>
  <td>{float(row['median_latency_s']):.2f}s</td>
</tr>'''
        )
    return "\n".join(rows)


def render(records: list[dict[str, str]]) -> str:
    template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SparkBench v6.7.1 · One DGX Spark Leaderboard</title>
<link rel="canonical" href="https://wesche.com/dgx/">
<meta name="description" content="29 qualified local LLM deployments compared on one NVIDIA DGX Spark with the SparkBench v6.7.1 challenge contract.">
<meta property="og:title" content="SparkBench v6.7.1 · One DGX Spark">
<meta property="og:description" content="29 qualified deployments, one fixed contract, complete public evidence.">
<meta property="og:image" content="https://wesche.com/dgx/spark-bench-promo.jpg">
<meta property="og:url" content="https://wesche.com/dgx/">
<meta property="og:type" content="website">
<style>
:root{--bg:#0b0d12;--panel:#12151c;--line:#2a2f3a;--fg:#f2f4f8;--mut:#a0a7b4;--cyan:#65c7d0;--green:#67d391;--amber:#e9b85f;--red:#ef7b72}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;letter-spacing:0}
a{color:inherit}.wrap{max-width:1180px;margin:auto;padding:0 20px}.mast{border-bottom:1px solid var(--line);background:#0e1117}
.mast .wrap{min-height:118px;display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{display:flex;align-items:center;gap:16px}.brand img{width:132px;height:74px;object-fit:cover;border:1px solid var(--line);border-radius:6px}
.eyebrow{color:var(--cyan);font-size:12px;font-weight:700}.brand h1{font-size:28px;line-height:1.1;margin:3px 0 5px}.brand p{margin:0;color:var(--mut)}.links{display:flex;gap:8px}.links a{padding:8px 11px;border:1px solid var(--line);border-radius:6px;text-decoration:none;font-weight:650}.links a:hover{border-color:var(--cyan)}
.summary{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--line)}.metric{padding:17px 18px;border-right:1px solid var(--line)}.metric:last-child{border-right:0}.metric b{display:block;font-size:22px}.metric span{color:var(--mut);font-size:12px}
main{padding:24px 0 48px}.intro{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:16px}.intro h2{font-size:20px;margin:0 0 5px}.intro p{margin:0;color:var(--mut);max-width:760px}
.controls{display:flex;gap:10px;align-items:center;margin:18px 0 12px;flex-wrap:wrap}.search{flex:1;min-width:220px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:9px 11px;font:inherit}.search:focus{outline:2px solid var(--cyan);outline-offset:1px}
.segments{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}.segments button{border:0;border-right:1px solid var(--line);background:var(--panel);color:var(--mut);padding:9px 12px;font:600 13px system-ui;cursor:pointer}.segments button:last-child{border-right:0}.segments button.active{background:var(--cyan);color:#071114}.count{color:var(--mut);font-size:12px;min-width:92px;text-align:right}
.table-wrap{overflow:auto;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}table{width:100%;border-collapse:collapse;min-width:850px}th{text-align:left;color:var(--mut);font-size:11px;font-weight:700;padding:10px;border-bottom:1px solid var(--line);background:#0e1117;position:sticky;top:0}td{padding:11px 10px;border-bottom:1px solid #1f232c;font-variant-numeric:tabular-nums}tbody tr:hover{background:#10141b}.rank{color:var(--mut);width:42px}.model{min-width:310px}.model a{display:block;font-weight:720;text-decoration:none}.model a:hover{color:var(--cyan)}.model span{display:block;color:var(--mut);font-size:11px;margin-top:2px}.score{font-size:17px}.score.top{color:var(--green)}.score.mid{color:var(--amber)}.score.low{color:var(--red)}.bar{display:block;width:74px;height:3px;background:#252b35;margin-top:4px}.bar b{display:block;height:100%;background:var(--cyan)}
.method{margin-top:26px;padding-top:22px;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:28px}.method h2{font-size:17px;margin:0 0 8px}.method p,.method li{color:var(--mut)}.method ul{margin:8px 0 0;padding-left:18px}.method code{color:var(--fg)}footer{border-top:1px solid var(--line);padding:18px 0;color:var(--mut);font-size:12px}
@media(max-width:720px){.mast .wrap{align-items:flex-start;flex-direction:column;padding-top:18px;padding-bottom:18px}.brand img{display:none}.links{width:100%}.links a{flex:1;text-align:center}.summary{grid-template-columns:1fr 1fr}.metric:nth-child(2){border-right:0}.metric:nth-child(-n+2){border-bottom:1px solid var(--line)}.intro{display:block}.segments{width:100%;overflow:auto}.segments button{flex:1}.count{text-align:left}.method{grid-template-columns:1fr}}
</style>
</head>
<body>
<header class="mast"><div class="wrap"><div class="brand"><img src="spark-bench-promo.jpg" alt="SparkBench on NVIDIA DGX Spark"><div><div class="eyebrow">NVIDIA DGX Spark · Current Cohort</div><h1>SparkBench v6.7.1</h1><p>One Spark. One contract. Qualified results only.</p></div></div><nav class="links"><a href="https://github.com/Weschera/spark-bench">GitHub</a><a href="https://github.com/Weschera/spark-bench/tree/main/results/cohorts/2026-08-01-one-spark-v671">Evidence</a></nav></div></header>
<div class="wrap summary"><div class="metric"><b>29</b><span>qualified deployments</span></div><div class="metric"><b>40</b><span>attempted configurations</span></div><div class="metric"><b>20 × 3</b><span>scenarios and repeats</span></div><div class="metric"><b>1×</b><span>DGX Spark · TP1</span></div></div>
<main class="wrap"><section class="intro"><div><h2>Current one-Spark ranking</h2><p>All rows use the repaired <code>v6.7.1-challenge</code> contract at grader <code>11d21bf</code>. Older runs are intentionally omitted because different methodologies are not comparable.</p></div></section>
<div class="controls"><input id="search" class="search" type="search" placeholder="Search models or configurations" aria-label="Search leaderboard"><div class="segments" aria-label="Filter by engine"><button class="active" data-filter="all">All</button><button data-filter="vLLM">vLLM</button><button data-filter="llama.cpp">llama.cpp</button><button data-filter="DS4">DS4</button></div><span id="count" class="count">29 shown</span></div>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Deployment</th><th>TrueScore</th><th>Quality</th><th>Calibration</th><th>Reliability</th><th>Median latency</th></tr></thead><tbody>
__ROWS__
</tbody></table></div>
<section class="method"><div><h2>Qualification contract</h2><ul><li>12/12 golden gate and tool-call preflight</li><li>Three repeats at temperature 0.3</li><li>Thinking off where supported</li><li>Zero transport errors and complete artifacts</li><li>Clean quarantine status</li></ul></div><div><h2>Reading the score</h2><p>TrueScore is quality-dominant: quality 55%, calibration 25%, reliability 15%, and speed 5%. These are deployment results, so engine, quantization, context, and speculative mode are part of each measured configuration.</p><p>Two quarantined and nine aborted attempts remain in the public evidence archive, but are not ranked here.</p></div></section>
</main>
<footer><div class="wrap">SparkBench v6.7.1 challenge cohort · 20 scenarios across 10 domains · updated __UPDATED__ · <a href="https://github.com/Weschera/spark-bench">source and full history</a></div></footer>
<script>
const rows=[...document.querySelectorAll('tbody tr')],search=document.querySelector('#search'),count=document.querySelector('#count'),buttons=[...document.querySelectorAll('[data-filter]')];let engine='all';
function apply(){const q=search.value.trim().toLowerCase();let n=0;rows.forEach(r=>{const show=(engine==='all'||r.dataset.engine===engine)&&(!q||r.dataset.search.includes(q));r.hidden=!show;if(show)n++});count.textContent=n+' shown'}
search.addEventListener('input',apply);buttons.forEach(b=>b.addEventListener('click',()=>{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');engine=b.dataset.filter;apply()}));
</script>
</body></html>'''
    return template.replace("__ROWS__", render_rows(records)).replace("__UPDATED__", date.today().isoformat())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("qualified_tsv", type=Path)
    parser.add_argument("output_html", type=Path)
    args = parser.parse_args()
    with args.qualified_tsv.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle, delimiter="\t"))
    if not records or any(row["status"] != "qualified" for row in records):
        raise SystemExit("input must contain qualified rows only")
    ranks = [int(row["rank"]) for row in records]
    if ranks != list(range(1, len(records) + 1)):
        raise SystemExit("input ranks are not contiguous")
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(render(records), encoding="utf-8")
    print(f"wrote {args.output_html}: {len(records)} qualified rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
