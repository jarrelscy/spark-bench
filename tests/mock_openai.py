#!/usr/bin/env python3
"""Minimal OpenAI-compatible mock server for harness testing. NO model, NO GPU —
canned streaming responses only, so gates/preflight/quarantine can be exercised
end-to-end without touching a live box.

Modes:
  good        : answers tool prompts with ONE structured tool_call
                (get_weather Paris), then plain text on later turns.
  dead-parser : never emits tool_calls — emulates a wrong --tool-call-parser
                (fluent text claiming success). The v5 failure mode.

Usage: mock_openai.py --port 8399 --model-id gemma-test --mode good
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

ARGS = None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silence request logging
        pass

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            body = json.dumps({"object": "list",
                               "data": [{"id": ARGS.model_id, "object": "model"}]})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        msgs = req.get("messages", [])
        has_tools = bool(req.get("tools"))
        seen_tool_result = any(m.get("role") == "tool" for m in msgs)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()

        def chunk(delta, finish=None):
            obj = {"id": "mock", "object": "chat.completion.chunk",
                   "choices": [{"index": 0, "delta": delta,
                                "finish_reason": finish}]}
            self.wfile.write(f"data: {json.dumps(obj)}\n\n".encode())

        if ARGS.mode == "good" and has_tools and not seen_tool_result:
            chunk({"tool_calls": [{"index": 0, "id": "call_0", "type": "function",
                                   "function": {"name": "get_weather",
                                                "arguments": ""}}]})
            chunk({"tool_calls": [{"index": 0,
                                   "function": {"arguments": '{"city": "Paris"}'}}]})
            chunk({}, finish="tool_calls")
        else:
            chunk({"content": "I have completed all the requested steps."})
            chunk({}, finish="stop")
        usage = {"id": "mock", "object": "chat.completion.chunk", "choices": [],
                 "usage": {"prompt_tokens": 50, "completion_tokens": 10}}
        self.wfile.write(f"data: {json.dumps(usage)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")


def main():
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--mode", choices=["good", "dead-parser"], default="good")
    ARGS = ap.parse_args()
    srv = HTTPServer(("127.0.0.1", ARGS.port), H)
    print(f"mock openai on :{ARGS.port} model={ARGS.model_id} mode={ARGS.mode}",
          flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
