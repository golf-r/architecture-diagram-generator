import http.client
import importlib.util
import io
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "pptx_server.py"
EXAMPLE_SVG = Path(__file__).resolve().parents[2] / "examples" / "architecture-diagram-overview.svg"


def load_server_module():
    spec = importlib.util.spec_from_file_location("pptx_server", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PptxServerTests(unittest.TestCase):
    def setUp(self):
        try:
            import pptx  # noqa: F401
        except ImportError:
            self.skipTest("python-pptx not installed")
        self.module = load_server_module()
        self.server = self.module.ThreadingHTTPServer(("127.0.0.1", 0), self.module.Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _get(self, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("GET", path)
        r = conn.getresponse()
        body = r.read()
        conn.close()
        return r.status, body

    def test_health(self):
        status, body = self._get("/health")
        self.assertEqual(status, 200)
        self.assertIn(b'"ok"', body)

    def test_export_returns_pptx(self):
        svg = EXAMPLE_SVG.read_text(encoding="utf-8")
        conn = http.client.HTTPConnection("127.0.0.1", self.port)
        conn.request("POST", "/export", body=svg.encode("utf-8"),
                     headers={"Content-Type": "image/svg+xml"})
        r = conn.getresponse()
        data = r.read()
        conn.close()
        self.assertEqual(r.status, 200)
        self.assertEqual(data[:2], b"PK", "response is not a zip")
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            self.assertIn("ppt/slides/slide1.xml", zf.namelist())


if __name__ == "__main__":
    unittest.main()
