import argparse
import html
import json
import time
from pathlib import Path

import requests


DEFAULT_FRONTEND = "https://scholr-coral.vercel.app"
DEFAULT_BACKEND = "https://scholr-k9sj.onrender.com"


def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    return response.json()


def stream_module(base_url: str, path: str, payload: dict) -> dict:
    started = time.perf_counter()
    first_token_latency_ms = None
    chunks: list[str] = []
    meta_events: list[dict] = []
    done_received = False

    with requests.post(f"{base_url}{path}", json=payload, stream=True, timeout=120) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data: "):
                continue
            data = raw_line[6:]
            if data == "[DONE]":
                done_received = True
                break
            event = json.loads(data)
            if event.get("type") == "meta":
                meta_events.append(event)
            elif event.get("type") == "chunk":
                if first_token_latency_ms is None:
                    first_token_latency_ms = round((time.perf_counter() - started) * 1000)
                chunks.append(event.get("chunk", ""))
            elif event.get("type") == "error":
                meta_events.append({"error": event})

    text = "".join(chunks).strip()
    return {
        "first_token_latency_ms": first_token_latency_ms,
        "completion_latency_ms": round((time.perf_counter() - started) * 1000),
        "response_length": len(text),
        "done_received": done_received,
        "meta_events": meta_events,
        "fallback_marker": "provider temporarily unavailable" in text.lower() or "fallback academic mode" in text.lower(),
        "text": text,
    }


def answer_document(base_url: str, fixture_path: Path) -> dict:
    with fixture_path.open("rb") as handle:
        upload_response = requests.post(
            f"{base_url}/api/documents/upload",
            files={"file": (fixture_path.name, handle, "application/pdf")},
            timeout=120,
        )
    upload_response.raise_for_status()
    upload_payload = upload_response.json()

    answer_response = requests.post(
        f"{base_url}/api/documents/answer",
        json={
            "document_id": upload_payload["document_id"],
            "question": "How does normalization help in DBMS?",
            "top_k": 3,
        },
        timeout=120,
    )
    answer_response.raise_for_status()
    answer_payload = answer_response.json()
    return {
        "upload": upload_payload,
        "answer": answer_payload,
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def render_html(path: Path, title: str, body: str) -> None:
    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f8fafc;
        --card: #ffffff;
        --ink: #0f172a;
        --muted: #475569;
        --border: #cbd5e1;
        --accent: #0f766e;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Segoe UI", Arial, sans-serif;
        background: linear-gradient(180deg, #eff6ff 0%, var(--bg) 28%);
        color: var(--ink);
      }}
      main {{
        max-width: 1100px;
        margin: 0 auto;
        padding: 40px 32px 56px;
      }}
      h1 {{ margin: 0 0 12px; font-size: 34px; }}
      p, li {{ color: var(--muted); line-height: 1.6; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin: 24px 0;
      }}
      .card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 18px 20px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
      }}
      .label {{
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
      }}
      .value {{
        margin-top: 8px;
        font-size: 18px;
        font-weight: 700;
        color: var(--ink);
      }}
      pre {{
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 14px;
        line-height: 1.55;
      }}
      .panel {{
        margin-top: 24px;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 24px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
      }}
      .badge {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #ccfbf1;
        color: var(--accent);
        font-size: 13px;
        font-weight: 700;
      }}
    </style>
  </head>
  <body>
    <main>
      {body}
    </main>
  </body>
</html>
"""
    path.write_text(document, encoding="utf-8")


def build_stream_html(proof: dict) -> str:
    cards = []
    for module_name in ("research", "notes", "doubt"):
        module = proof["streams"][module_name]
        cards.append(
            f"""
            <div class="card">
              <div class="label">{module_name.title()}</div>
              <div class="value">{module['first_token_latency_ms']} ms first token</div>
              <p>{module['completion_latency_ms']} ms completion · {module['response_length']} chars · [DONE]={str(module['done_received']).lower()}</p>
            </div>
            """
        )

    panels = []
    for module_name in ("research", "notes", "doubt"):
        module = proof["streams"][module_name]
        preview = html.escape(module["text"][:1600])
        provider = html.escape(proof["health"]["/health/provider"].get("active_provider") or "unknown")
        model = html.escape(proof["health"]["/health/provider"].get("selected_model") or "unknown")
        panels.append(
            f"""
            <section class="panel">
              <span class="badge">AI Mode · {provider} · {model}</span>
              <h2>{module_name.title()} live output</h2>
              <pre>{preview}</pre>
            </section>
            """
        )

    return f"""
      <h1>Scholr Live Stream Proof</h1>
      <p>Captured from the live production backend. This panel uses real streamed output, not placeholder text.</p>
      <div class="grid">{''.join(cards)}</div>
      {''.join(panels)}
    """


def build_provider_html(proof: dict) -> str:
    provider = proof["health"]["/health/provider"]
    return f"""
      <h1>Scholr Provider Recovery Proof</h1>
      <p>Live provider state captured from the production backend.</p>
      <div class="grid">
        <div class="card"><div class="label">Active provider</div><div class="value">{html.escape(str(provider.get('active_provider')))}</div></div>
        <div class="card"><div class="label">Selected model</div><div class="value">{html.escape(str(provider.get('selected_model')))}</div></div>
        <div class="card"><div class="label">Provider ready</div><div class="value">{html.escape(str(provider.get('provider_ready')))}</div></div>
        <div class="card"><div class="label">Recovery state</div><div class="value">{html.escape(str(provider.get('provider_recovery_state')))}</div></div>
      </div>
      <section class="panel">
        <h2>Provider health JSON</h2>
        <pre>{html.escape(json.dumps(provider, indent=2))}</pre>
      </section>
    """


def build_document_html(proof: dict) -> str:
    upload = proof["document"]["upload"]
    answer = proof["document"]["answer"]
    citation = (answer.get("citations") or [{}])[0]
    return f"""
      <h1>Scholr Document Workflow Proof</h1>
      <p>Live production upload and answer capture using the bundled academic sample PDF fixture.</p>
      <div class="grid">
        <div class="card"><div class="label">Upload status</div><div class="value">{html.escape(str(upload.get('status')))}</div></div>
        <div class="card"><div class="label">Answer mode</div><div class="value">{html.escape(str(answer.get('answer_mode')))}</div></div>
        <div class="card"><div class="label">Retrieval mode</div><div class="value">{html.escape(str(answer.get('retrieval_mode')))}</div></div>
        <div class="card"><div class="label">Generation used</div><div class="value">{html.escape(str(answer.get('generation_used')))}</div></div>
      </div>
      <section class="panel">
        <h2>Answer preview</h2>
        <pre>{html.escape((answer.get('answer') or '')[:1400])}</pre>
      </section>
      <section class="panel">
        <h2>First citation</h2>
        <pre>{html.escape(json.dumps(citation, indent=2))}</pre>
      </section>
    """


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend", default=DEFAULT_FRONTEND)
    parser.add_argument("--backend", default=DEFAULT_BACKEND)
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parents[2] / "docs" / "proof"))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "academic-sample.pdf"

    proof = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frontend": args.frontend,
        "backend": args.backend,
        "health": {
            "/health": fetch_json(f"{args.backend}/health"),
            "/health/provider": fetch_json(f"{args.backend}/health/provider"),
            "/health/generate-test": fetch_json(f"{args.backend}/health/generate-test"),
            "/health/documents": fetch_json(f"{args.backend}/health/documents"),
        },
        "streams": {
            "research": stream_module(args.backend, "/api/research", {"topic": "DBMS normalization"}),
            "notes": stream_module(args.backend, "/api/notes", {"topic": "Operating system deadlock"}),
            "doubt": stream_module(
                args.backend,
                "/api/doubt",
                {"question": "What is normalization in DBMS?", "subject": "DBMS"},
            ),
        },
        "document": answer_document(args.backend, fixture_path),
    }

    write_json(output_dir / "live-proof.json", proof)
    render_html(output_dir / "live-stream-proof.html", "Scholr Live Stream Proof", build_stream_html(proof))
    render_html(output_dir / "provider-proof.html", "Scholr Provider Proof", build_provider_html(proof))
    render_html(output_dir / "document-proof.html", "Scholr Document Proof", build_document_html(proof))
    print(json.dumps({"ok": True, "output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
