import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "svg_quality_checker.py"


def load_checker_module():
    spec = importlib.util.spec_from_file_location("svg_quality_checker", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SVGQualityCheckerTests(unittest.TestCase):
    def test_html_template_with_expected_structure_passes(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        html = """<!DOCTYPE html>
<html lang="zh-CN">
<body>
  <div class="container" id="report-container">
    <div class="toolbar">
      <button class="toolbar-btn" onclick="copyMermaid(this)">Mermaid</button>
      <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
      <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
      <button class="toolbar-btn" onclick="downloadPPTX(this)">导出 PPTX</button>
    </div>
    <svg viewBox="0 0 1000 600" width="1000" height="600" role="img" aria-label="架构图">
      <rect x="10" y="10" width="100" height="50" />
    </svg>
    <pre class="mermaid-src" style="display:none">flowchart TD
A-->B
</pre>
  </div>
</body>
</html>"""

        result = checker.check_html_content(html, source_path=Path("diagram.html"))

        self.assertTrue(result["passed"])
        self.assertEqual(result["errors"], [])

    def test_html_template_missing_toolbar_and_mermaid_source_fails(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        html = """<!DOCTYPE html>
<html lang="zh-CN">
<body>
  <div class="container" id="report-container">
    <svg viewBox="0 0 1000 600" width="1000" height="600" role="img" aria-label="架构图">
      <rect x="10" y="10" width="100" height="50" />
    </svg>
  </div>
</body>
</html>"""

        result = checker.check_html_content(html, source_path=Path("diagram.html"))

        self.assertFalse(result["passed"])
        self.assertTrue(any("toolbar" in error for error in result["errors"]))
        self.assertTrue(any("mermaid" in error.lower() for error in result["errors"]))

    def test_svg_with_script_and_missing_viewbox_fails(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg width="1000" height="600" xmlns="http://www.w3.org/2000/svg">
  <script>console.log('x')</script>
  <rect x="10" y="10" width="100" height="50" />
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertFalse(result["passed"])
        self.assertTrue(any("viewBox" in error for error in result["errors"]))
        self.assertTrue(any("script" in error.lower() for error in result["errors"]))

    def test_long_text_warns_about_overflow_risk(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 1000 600" width="1000" height="600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <text x="40" y="40">This is a very long component label that should be flagged</text>
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("overflow" in warning.lower() for warning in result["warnings"]))

    def test_arrow_crossing_rect_fails(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <rect x="120" y="80" width="120" height="60" />
  <line x1="20" y1="110" x2="340" y2="110" marker-end="url(#a-gray)" />
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertFalse(result["passed"])
        self.assertTrue(any("cross" in error.lower() or "intersect" in error.lower() for error in result["errors"]))

    def test_mermaid_svg_label_mismatch_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        html = """<!DOCTYPE html>
<html lang="zh-CN">
<body>
  <div class="container" id="report-container">
    <div class="toolbar">
      <button class="toolbar-btn" onclick="copyMermaid(this)">Mermaid</button>
      <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
      <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
      <button class="toolbar-btn" onclick="downloadPPTX(this)">导出 PPTX</button>
    </div>
    <svg viewBox="0 0 1000 600" width="1000" height="600" role="img" aria-label="架构图">
      <text x="120" y="120">Gamma</text>
    </svg>
    <pre class="mermaid-src" style="display:none">flowchart TD
A[Alpha] --> B[Beta]
</pre>
  </div>
</body>
</html>"""

        result = checker.check_html_content(html, source_path=Path("diagram.html"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("mermaid" in warning.lower() for warning in result["warnings"]))

    def test_html_missing_pptx_button_fails(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        html = """<!DOCTYPE html>
<html lang="zh-CN">
<body>
  <div class="container" id="report-container">
    <div class="toolbar">
      <button class="toolbar-btn" onclick="copyMermaid(this)">Mermaid</button>
      <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
      <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
    </div>
    <svg viewBox="0 0 1000 600" width="1000" height="600" role="img" aria-label="架构图">
      <rect x="10" y="10" width="100" height="50" />
    </svg>
    <pre class="mermaid-src" style="display:none">flowchart TD
A-->B
</pre>
  </div>
</body>
</html>"""

        result = checker.check_html_content(html, source_path=Path("diagram.html"))

        self.assertFalse(result["passed"])
        self.assertTrue(any("PPTX" in error for error in result["errors"]))

    def test_arrow_endpoint_distance_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <rect x="120" y="80" width="120" height="60" />
  <line x1="20" y1="110" x2="118" y2="110" marker-end="url(#a-gray)" />
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("endpoint" in warning.lower() or "distance" in warning.lower() for warning in result["warnings"]))

    def test_unused_marker_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <defs>
    <marker id="a-gray" markerWidth="8" markerHeight="5.5" refX="7" refY="2.75" orient="auto">
      <polygon points="0 0, 8 2.75, 0 5.5" />
    </marker>
  </defs>
  <rect x="120" y="80" width="120" height="60" />
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("marker" in warning.lower() or "defs" in warning.lower() for warning in result["warnings"]))

    def test_small_spacing_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <rect x="20" y="40" width="120" height="60" />
  <rect x="152" y="40" width="120" height="60" />
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("spacing" in warning.lower() or "gap" in warning.lower() for warning in result["warnings"]))

    def test_title_placement_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <text x="20" y="160">架构图</text>
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("title" in warning.lower() or "top" in warning.lower() for warning in result["warnings"]))

    def test_legend_and_annotation_placement_warns(self):
        module = load_checker_module()
        checker = module.SVGQualityChecker()

        svg = """<svg viewBox="0 0 400 300" width="400" height="300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <rect x="60" y="60" width="120" height="60" />
  <text x="80" y="110">说明：这里是注释</text>
  <text x="20" y="20">图例</text>
</svg>"""

        result = checker.check_svg_content(svg, source_path=Path("diagram.svg"))

        self.assertTrue(result["passed"])
        self.assertTrue(any("legend" in warning.lower() for warning in result["warnings"]))
        self.assertTrue(any("annotation" in warning.lower() or "note" in warning.lower() for warning in result["warnings"]))

    def test_publish_mode_fails_on_warning(self):
        module = load_checker_module()
        svg = """<svg viewBox="0 0 400 200" width="400" height="200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="架构图">
  <text x="20" y="160">架构图</text>
</svg>"""

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "diagram.svg"
            path.write_text(svg, encoding="utf-8")

            checker = module.SVGQualityChecker()
            result = checker.check_file(path)

            exit_code = 1 if result.warnings else 0
            if result.warnings:
                result.errors.append("Publish mode treats warnings as errors")

        self.assertEqual(exit_code, 1)
        self.assertTrue(any("title" in warning.lower() for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
