#!/usr/bin/env python3
"""Local HTTP bridge so the diagram's "导出 PPTX" browser button can invoke
the Python converter. Browsers cannot run Python directly, so the HTML page
POSTs the serialized SVG here and receives a .pptx blob.

Run once:  python scripts/pptx_server.py
Then any diagram's "导出 PPTX" button works (it calls http://localhost:8765).
"""

from __future__ import annotations

import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from export_pptx import convert_svg_to_pptx  # noqa: E402

PORT = 8765
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
            msg = f'{{"error":"{exc}"}}'.encode("utf-8")
            self._send(500, msg, "application/json")

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[pptx_server] {self.address_string()} {fmt % args}\n")


def main() -> int:
    try:
        import pptx  # noqa: F401
    except ImportError:
        print("ERROR: python-pptx is not installed. Run: pip install -r requirements.txt",
              file=sys.stderr)
        return 2
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"PPTX export server listening on http://localhost:{PORT}")
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
