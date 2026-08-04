#!/usr/bin/env python3
"""Local HTTP bridge so the diagram's "导出 PPTX" browser button can invoke
the Python converter. Browsers cannot run Python directly, so the HTML page
POSTs the serialized SVG here and receives a .pptx blob.

Run:  python scripts/pptx_server.py [--port N]
Reuses an already-running instance; if the requested port (default 8765) is
taken by another app, auto-selects the next free port and prints
`PPTX_EXPORT_PORT=<port>` so the caller can inject it into the HTML.
The architecture-diagram skill starts this in the background after generating
a diagram HTML, so the "导出 PPTX" button works out of the box.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import tempfile
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from export_pptx import convert_svg_to_pptx  # noqa: E402

DEFAULT_PORT = 8765
CORS_HEADERS = [
    ("Access-Control-Allow-Origin", "*"),
    ("Access-Control-Allow-Methods", "POST, OPTIONS, GET"),
    ("Access-Control-Allow-Headers", "Content-Type"),
]
PPTX_CT = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # CORS preflight
        self.send_response(204)
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            try:
                import pptx  # noqa: F401
                self._send(200, b'{"ok":true}', "application/json")
            except ImportError:
                self._send(200, b'{"ok":false,"error":"python-pptx not installed"}',
                           "application/json")
        else:
            self._send(404, b'{"error":"not found"}', "application/json")

    def do_POST(self) -> None:
        if self.path != "/export":
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            svg_text = (self.rfile.read(length) if length else b"").decode("utf-8", "replace")
            if not svg_text.strip():
                self._send(400, b'{"error":"empty SVG body"}', "application/json")
                return
            with tempfile.TemporaryDirectory() as tmp_dir:
                svg_path = Path(tmp_dir) / "in.svg"
                svg_path.write_text(svg_text, encoding="utf-8")
                out_path = Path(tmp_dir) / "out.pptx"
                convert_svg_to_pptx(svg_path, out_path)
                pptx_bytes = out_path.read_bytes()
            self._send(200, pptx_bytes, PPTX_CT)
        except Exception as exc:  # noqa: BLE001
            msg = json.dumps({"error": str(exc)}).encode("utf-8")
            self._send(500, msg, "application/json")

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[pptx_server] {self.address_string()} {fmt % args}\n")


def find_free_port(start: int, count: int = 20) -> int | None:
    """Return the first port in [start, start+count) that can be bound, else None."""
    for port in range(start, start + count):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return None


def server_already_running(port: int) -> bool:
    """True if our pptx_server is already serving on `port` (GET /health -> {"ok":true})."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
            return r.status == 200 and b'"ok":true' in r.read()
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Local PPTX export server for the architecture-diagram skill"
    )
    parser.add_argument(
        "-p", "--port", type=int,
        default=int(os.environ.get("PPTX_PORT", str(DEFAULT_PORT))),
        help=f"port to listen on (default {DEFAULT_PORT}, or $PPTX_PORT)",
    )
    args = parser.parse_args(argv)

    try:
        import pptx  # noqa: F401
    except ImportError:
        print("ERROR: python-pptx is not installed. "
              "Run: pip install -r architecture-diagram/requirements.txt", file=sys.stderr)
        return 2

    # Reuse an already-running instance on the requested port.
    if server_already_running(args.port):
        print(f"pptx_server already running on http://localhost:{args.port} - reusing.")
        print(f"PPTX_EXPORT_PORT={args.port}")
        return 0

    # The requested port may be taken by another app; auto-pick a free one.
    port = find_free_port(args.port, count=20)
    if port is None:
        print(f"ERROR: no free port in {args.port}-{args.port + 19}. "
              f"Pass --port <n> or set PPTX_PORT.", file=sys.stderr)
        return 1

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    # Machine-parseable line so the calling agent can learn the actual port.
    print(f"PPTX_EXPORT_PORT={port}")
    print(f"PPTX export server listening on http://localhost:{port}")
    print("  POST /export   (body = SVG XML) -> .pptx")
    print("  GET  /health")
    print("  Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
