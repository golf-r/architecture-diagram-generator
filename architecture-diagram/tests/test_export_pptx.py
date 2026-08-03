import contextlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "export_pptx.py"
EXAMPLE_SVG = Path(__file__).resolve().parents[2] / "examples" / "architecture-diagram-overview.svg"


def load_export_module():
    spec = importlib.util.spec_from_file_location("export_pptx", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExportPptxTests(unittest.TestCase):
    def setUp(self):
        try:
            import pptx  # noqa: F401
        except ImportError:
            self.skipTest("python-pptx not installed")

    def test_convert_example_svg_to_pptx(self):
        module = load_export_module()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.pptx"
            module.convert_svg_to_pptx(EXAMPLE_SVG, out)
            self.assertTrue(out.exists() and out.stat().st_size > 0, "pptx not written")
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
                self.assertIn("ppt/slides/slide1.xml", names)
                slide_xml = zf.read("ppt/slides/slide1.xml").decode("utf-8")
            # Rounded corners (rx rects) preserved as native roundRect
            self.assertIn("roundRect", slide_xml)
            # Dashed borders (stroke-dasharray="5,3") preserved
            self.assertTrue("custDash" in slide_xml or "prstDash" in slide_xml,
                            "dash style not preserved")

    def test_preprocess_resolves_percent_width(self):
        module = load_export_module()
        svg = '<svg viewBox="0 0 1080 760"><rect width="100%" height="100%" fill="#fff"/></svg>'
        out = module._preprocess_svg(svg, 1080, 760)
        self.assertNotIn("100%", out)
        self.assertIn('width="1080"', out)

    def test_main_html_input_produces_pptx(self):
        module = load_export_module()
        svg = ('<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
               '<rect x="10" y="10" width="50" height="30" rx="4" fill="#eaf0fa" '
               'stroke="#5a82c2"/></svg>')
        html = f"<!DOCTYPE html><html><body>{svg}</body></html>"
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "in.html"
            html_path.write_text(html, encoding="utf-8")
            out = Path(tmp) / "out.pptx"
            rc = module.main([str(html_path), "-o", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists() and out.stat().st_size > 0)

    def test_main_html_without_svg_returns_error(self):
        module = load_export_module()
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "bad.html"
            html_path.write_text("<!DOCTYPE html><html><body>no svg here</body></html>",
                                 encoding="utf-8")
            out = Path(tmp) / "out.pptx"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = module.main([str(html_path), "-o", str(out)])
            self.assertEqual(rc, 1)
            self.assertIn("ERROR", err.getvalue())
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
