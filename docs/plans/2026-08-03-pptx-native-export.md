# PPTX 原生导出 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a one-click "导出 PPTX" button to the architecture-diagram skill that produces a native, editable PowerPoint file (rounded corners / dashed borders / arrowheads preserved as DrawingML shapes), by vendoring ppt-master's SVG→DrawingML converter core and bridging it to the browser via a local Python HTTP server.

**Architecture:** Vendor ppt-master's self-contained `drawingml_*` converter core (stdlib-only) into `architecture-diagram/scripts/svg_to_pptx/`. Write a thin `export_pptx.py` (python-pptx packaging: empty PPTX skeleton → unzip → overwrite `slide1.xml` with the converter's output → rezip). Add a stdlib `pptx_server.py` HTTP bridge so the browser button (added to `template.html`) can POST the SVG and receive a `.pptx`. Animations/narration are trimmed; rgba color migration is deferred (known limitation: the converter doesn't parse `rgba()`).

**Tech Stack:** Python 3 (stdlib `http.server`, `zipfile`, `xml.etree`), `python-pptx>=0.6.21`, vanilla browser JS (fetch + Blob). Tests: `unittest` (matches existing style).

**Design doc:** `docs/plans/2026-08-03-pptx-native-export-design.md` (approved).

**Key facts established from reading ppt-master's code:**
- `convert_svg_to_slide_shapes(svg_path, slide_num=1, verbose=False)` returns `(slide_xml, media_files, rel_entries, anim_targets)` where `slide_xml` is a **complete valid `<p:sld>` document** (with `<p:clrMapOvr><a:masterClrMapping/>`) — write it directly to `ppt/slides/slide1.xml`.
- The `drawingml_*` modules import only each other + stdlib (verified). Animations/narration live in `pptx_builder/cli/media/notes/narration/animation` which we do NOT vendor.
- `tspan_flattener.py` (in ppt-master) hard-imports ppt-master's separate `svg_finalize` package → we replace it with a **no-op stub** (architecture-diagram SVGs use plain `<text>`, no positional `<tspan>`).
- `drawingml_converter.py` calls `use_expander` only inside `if icons_dir.exists()` — that dir won't exist here, so it's dead code, but we vendor `use_expander.py` anyway (stdlib-only, cheap insurance).
- Mapping guarantees: `<rect rx>`→`prst="roundRect"` (adj=`round(rx/min(w,h)*100000)`, cap 50000); `stroke-dasharray="5,3"`→`<a:custDash>`; `<marker>`→`<a:tailEnd type="triangle">`; `1px=9525 EMU`; `font-size px→pt ×0.75`.
- Packaging (from `pptx_builder.py:447-460,854-860`): `Presentation()` → set slide_width/height → `add_slide(layouts[6])` → save temp `base.pptx` → `zipfile.extractall` → overwrite `slide1.xml` → rezip with `ZIP_DEFLATED` over `rglob`. Content-types patching only fires for media/notes (none here) — skip it.

---

### Task 1: Vendor the svg_to_pptx converter core + requirements.txt

**Files:**
- Create: `architecture-diagram/scripts/svg_to_pptx/__init__.py`
- Create: `architecture-diagram/scripts/svg_to_pptx/tspan_flattener.py` (no-op stub, NOT copied from ppt-master)
- Copy from ppt-master → `architecture-diagram/scripts/svg_to_pptx/`: `drawingml_context.py`, `drawingml_utils.py`, `drawingml_paths.py`, `drawingml_styles.py`, `drawingml_elements.py`, `drawingml_converter.py`, `use_expander.py`
- Create: `architecture-diagram/requirements.txt`

**Step 1: Copy the 7 verbatim files from ppt-master**

Run (Git Bash):
```bash
SRC="C:/Users/shichenchen/.claude/skills/ppt-master/scripts/svg_to_pptx"
DST="D:/architecture-diagram-generator/architecture-diagram/scripts/svg_to_pptx"
mkdir -p "$DST"
cp "$SRC/drawingml_context.py" "$SRC/drawingml_utils.py" "$SRC/drawingml_paths.py" "$SRC/drawingml_styles.py" "$SRC/drawingml_elements.py" "$SRC/drawingml_converter.py" "$SRC/use_expander.py" "$DST/"
ls "$DST"
```
Expected: 7 files listed. **Do NOT copy** `__init__.py`, `tspan_flattener.py`, `pptx_builder.py`, `pptx_cli.py`, `pptx_media.py`, `pptx_notes.py`, `pptx_narration.py`, `animation_config.py`, `pptx_slide_xml.py`, `pptx_dimensions.py`, `pptx_discovery.py` from ppt-master.

**Step 2: Create the trimmed `__init__.py`**

Create `architecture-diagram/scripts/svg_to_pptx/__init__.py`:
```python
"""svg_to_pptx - vendored SVG -> DrawingML converter core (from ppt-master).

Only the conversion core is vendored (drawingml_* + helpers). Packaging,
CLI, animations, narration, notes and image-media were intentionally
trimmed - this skill's SVGs are simple (rect/text/line/path/marker) and
need none of them.

Public API:
    convert_svg_to_slide_shapes(svg_path, slide_num=1) -> (slide_xml, ...)
"""

from .drawingml_converter import convert_svg_to_slide_shapes

__all__ = ["convert_svg_to_slide_shapes"]
```

**Step 3: Create the no-op `tspan_flattener.py` stub**

Create `architecture-diagram/scripts/svg_to_pptx/tspan_flattener.py`:
```python
"""No-op tspan flattener (stub).

ppt-master's real tspan_flattener delegates to a separate svg_finalize
package that we did not vendor. architecture-diagram SVGs use plain
<text> elements (no positional <tspan> with x/y/dy), so flattening is
a no-op here. drawingml_converter calls flatten_positional_tspans()
unconditionally; this stub satisfies that call without the dependency.

If tspan support is ever needed, vendor ppt-master's
svg_finalize/flatten_tspan.py (and its deps) and replace this stub.
"""

from __future__ import annotations

from xml.etree import ElementTree as ET


def flatten_positional_tspans(tree: ET.ElementTree, merge_paragraphs: bool = False) -> bool:
    """No-op: architecture-diagram SVGs have no positional <tspan>. Returns False."""
    return False
```

**Step 4: Create `architecture-diagram/requirements.txt`**

```text
# architecture-diagram PPTX export dependency
# Used by scripts/export_pptx.py and scripts/pptx_server.py.
# The quality checker (svg_quality_checker.py) stays stdlib-only.
# Install:  pip install -r architecture-diagram/requirements.txt
python-pptx>=0.6.21
```

**Step 5: Verify the package imports (no python-pptx needed yet)**

Run:
```bash
cd D:/architecture-diagram-generator/architecture-diagram
python -c "import sys; sys.path.insert(0,'scripts'); from svg_to_pptx import convert_svg_to_slide_shapes; print('import ok')"
```
Expected output: `import ok`

If a `ModuleNotFoundError` for a non-vendored module appears, a `drawingml_*` file has a lazy import of something we didn't copy — grep the vendored files for `from .` / `import ` and stub or vendor the missing module. (Expected: none — verified the core is self-contained.)

**Step 6: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/scripts/svg_to_pptx architecture-diagram/requirements.txt
git commit -m "feat: vendor ppt-master SVG->DrawingML converter core

Trimmed package: drawingml_* + use_expander + tspan_flattener (no-op
stub, drops svg_finalize dep). No animations/narration/packaging.
__init__ exposes only convert_svg_to_slide_shapes.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: export_pptx.py — CLI + convert function (TDD)

**Files:**
- Create: `architecture-diagram/scripts/export_pptx.py`
- Test: `architecture-diagram/tests/test_export_pptx.py`

**Step 1: Install the dependency**

```bash
pip install -r D:/architecture-diagram-generator/architecture-diagram/requirements.txt
```
Expected: `Successfully installed python-pptx-...` (or "already satisfied").

**Step 2: Write the failing smoke test**

Create `architecture-diagram/tests/test_export_pptx.py`:
```python
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
```

**Step 3: Run test to verify it fails**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_export_pptx.py
```
Expected: FAIL / error — `FileNotFoundError` loading `export_pptx.py` (it doesn't exist yet).

**Step 4: Implement `export_pptx.py`**

Create `architecture-diagram/scripts/export_pptx.py`:
```python
#!/usr/bin/env python3
"""Export an architecture-diagram SVG (or HTML) to a native, editable PPTX.

Wraps the vendored svg_to_pptx converter (from ppt-master): each SVG
element becomes a native DrawingML shape, so rounded corners, dashed
borders and arrowheads survive as editable PowerPoint shapes.
(PowerPoint's own SVG-import -> convert-to-shape path drops them.)

Requires python-pptx:  pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

# Make the sibling svg_to_pptx package importable when run as a script.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from svg_to_pptx import convert_svg_to_slide_shapes  # noqa: E402

EMU_PER_PX = 9525
SVG_TAG_RE = re.compile(r"<svg\b.*?</svg>", re.IGNORECASE | re.DOTALL)


def _viewbox_size(svg_text: str) -> tuple[float, float]:
    """Return (width, height) in SVG px from the root viewBox."""
    m = re.search(r"<svg\b[^>]*\bviewBox\s*=\s*[\"']([^\"']+)[\"']", svg_text, re.IGNORECASE)
    if not m:
        raise ValueError("SVG has no viewBox; cannot size the slide")
    parts = m.group(1).replace(",", " ").split()
    if len(parts) != 4:
        raise ValueError(f"Unexpected viewBox: {m.group(1)}")
    return float(parts[2]), float(parts[3])


def _preprocess_svg(svg_text: str, w: float, h: float) -> str:
    """Normalize SVG for the converter: resolve 100% width/height to viewBox px.

    The converter parses width/height as floats; '100%' (used by the
    full-canvas background rects) would crash it. The grid <pattern> fill
    is left as-is (renders empty in PPTX - decorative, acceptable loss).
    """
    svg_text = re.sub(r'\bwidth\s*=\s*"100%"', f'width="{w:g}"', svg_text)
    svg_text = re.sub(r'\bheight\s*=\s*"100%"', f'height="{h:g}"', svg_text)
    return svg_text


def _extract_svg_from_html(html_text: str) -> str:
    m = SVG_TAG_RE.search(html_text)
    if not m:
        raise ValueError("No <svg> block found in HTML")
    return m.group(0)


def convert_svg_to_pptx(svg_path: Path, out_path: Path, verbose: bool = False) -> Path:
    """Convert one SVG file to a single-slide native PPTX at out_path."""
    svg_path = Path(svg_path)
    svg_text = svg_path.read_text(encoding="utf-8")
    w, h = _viewbox_size(svg_text)
    svg_text = _preprocess_svg(svg_text, w, h)
    width_emu = int(round(w * EMU_PER_PX))
    height_emu = int(round(h * EMU_PER_PX))

    from pptx import Presentation  # imported lazily so module import works without it

    tmp = Path(tempfile.mkdtemp())
    try:
        prs = Presentation()
        prs.slide_width = width_emu
        prs.slide_height = height_emu
        prs.slides.add_slide(prs.slide_layouts[6])  # blank layout

        base_pptx = tmp / "base.pptx"
        prs.save(str(base_pptx))

        extract_dir = tmp / "pptx_content"
        with zipfile.ZipFile(base_pptx, "r") as zf:
            zf.extractall(extract_dir)

        # Converter reads from a file path; write the preprocessed SVG out.
        pre_svg = tmp / "source.svg"
        pre_svg.write_text(svg_text, encoding="utf-8")

        slide_xml, _media, _rels, _anim = convert_svg_to_slide_shapes(
            pre_svg, slide_num=1, verbose=verbose
        )
        # No media/rels for this skill's SVGs (no <image>); just overwrite slide1.xml.
        (extract_dir / "ppt" / "slides" / "slide1.xml").write_text(slide_xml, encoding="utf-8")

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fp in extract_dir.rglob("*"):
                if fp.is_file():
                    zf.write(fp, fp.relative_to(extract_dir))
        return out_path
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export architecture-diagram SVG/HTML to a native editable PPTX"
    )
    parser.add_argument("input", help="Path to .svg or .html file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output .pptx path (default: <input>.pptx)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    try:
        import pptx  # noqa: F401
    except ImportError:
        print("ERROR: python-pptx is not installed. Run: pip install -r requirements.txt",
              file=sys.stderr)
        return 2

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 1

    if in_path.suffix.lower() in (".html", ".htm"):
        svg_text = _extract_svg_from_html(in_path.read_text(encoding="utf-8"))
        tmp_dir = Path(tempfile.mkdtemp())
        svg_path = tmp_dir / "extracted.svg"
        svg_path.write_text(svg_text, encoding="utf-8")
    else:
        svg_path = in_path

    out_path = Path(args.output) if args.output else in_path.with_suffix(".pptx")
    try:
        convert_svg_to_pptx(svg_path, out_path, verbose=args.verbose)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: conversion failed: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

> **If the smoke test fails on the grid pattern:** the example's `<rect fill="url(#grid)"/>` may trip the converter's pattern handling. If so, add to `_preprocess_svg` (before returning): `svg_text = re.sub(r'<rect\b[^>]*fill="url\(#grid\)"[^>]*/>', '', svg_text)` to strip the decorative grid rect. Re-run. The white `<rect fill="#ffffff"/>` is harmless (and the PPT slide background is white anyway).

**Step 5: Run test to verify it passes**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_export_pptx.py
```
Expected: `OK` (2 tests pass: the conversion produces a zip with `slide1.xml` containing `roundRect` and `custDash`/`prstDash`; preprocessing resolves `100%`).

Also verify the CLI end-to-end:
```bash
cd D:/architecture-diagram-generator/architecture-diagram
python scripts/export_pptx.py ../../examples/architecture-diagram-overview.svg -o /tmp/overview.pptx
```
Expected: `Wrote: /tmp/overview.pptx` (or a Windows temp path). Open the `.pptx` in PowerPoint to eyeball (manual — full acceptance in Task 7).

**Step 6: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/scripts/export_pptx.py architecture-diagram/tests/test_export_pptx.py
git commit -m "feat: add export_pptx.py CLI wrapping vendored converter

python-pptx skeleton -> unzip -> overwrite slide1.xml -> rezip.
Preprocesses 100% width/height to viewBox px. Smoke test asserts
roundRect + dash preserved on the example SVG.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: pptx_server.py — local HTTP bridge (TDD)

**Files:**
- Create: `architecture-diagram/scripts/pptx_server.py`
- Test: `architecture-diagram/tests/test_pptx_server.py`

**Step 1: Write the failing server test**

Create `architecture-diagram/tests/test_pptx_server.py`:
```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_pptx_server.py
```
Expected: FAIL / error — `FileNotFoundError` loading `pptx_server.py`.

**Step 3: Implement `pptx_server.py`**

Create `architecture-diagram/scripts/pptx_server.py`:
```python
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
            tmp_dir = Path(tempfile.mkdtemp())
            svg_path = tmp_dir / "in.svg"
            svg_path.write_text(svg_text, encoding="utf-8")
            out_path = tmp_dir / "out.pptx"
            convert_svg_to_pptx(svg_path, out_path)
            self._send(200, out_path.read_bytes(), PPTX_CT)
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
```

**Step 4: Run test to verify it passes**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_pptx_server.py
```
Expected: `OK` (2 tests pass: `/health` returns `{"ok":true}`; `/export` returns a zip containing `slide1.xml`).

**Step 5: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/scripts/pptx_server.py architecture-diagram/tests/test_pptx_server.py
git commit -m "feat: add pptx_server.py local HTTP bridge for browser button

stdlib http.server on localhost:8765; POST /export -> .pptx, GET /health.
CORS-enabled for file:// HTML. Reuses export_pptx.convert_svg_to_pptx.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: template.html — add "导出 PPTX" button + JS

**Files:**
- Modify: `architecture-diagram/resources/template.html`

**Step 1: Add the toolbar button**

Edit `architecture-diagram/resources/template.html`. Replace (toolbar block, ~lines 129-130):
```html
        <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
        <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
```
with:
```html
        <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
        <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
        <div class="toolbar-divider"></div>
        <button class="toolbar-btn" onclick="downloadPPTX(this)">导出 PPTX</button>
```

**Step 2: Add the `downloadPPTX()` JS function**

In the same file, insert before `async function copyMermaid(btn) {` (replace that anchor line):
```javascript
    async function downloadPPTX(btn) {
      const orig = btn.textContent;
      const SERVER = 'http://localhost:8765';
      let msg = '✗ 失败';
      try {
        const health = await fetch(SERVER + '/health');
        if (!health.ok) throw 0;
        const hj = await health.json();
        if (!hj.ok) { msg = '✗ 装依赖'; throw 0; }
        const resp = await fetch(SERVER + '/export', {
          method: 'POST',
          headers: { 'Content-Type': 'image/svg+xml;charset=utf-8' },
          body: serializeSvg()
        });
        if (!resp.ok) throw 0;
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'diagram.pptx';
        link.click();
        URL.revokeObjectURL(url);
        msg = '✓ 完成';
      } catch (e) {
        if (msg === '✗ 失败') msg = '✗ 先起服务';
      }
      btn.textContent = msg;
      setTimeout(function() { btn.textContent = orig; }, 2500);
    }

    async function copyMermaid(btn) {
```

**Step 3: Manual sanity check**

Open `architecture-diagram/resources/template.html` in a browser. Confirm the 4th "导出 PPTX" button renders. With the server NOT running, click it → button shows "✗ 先起服务". (Full happy-path check happens in Task 7.)

**Step 4: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/resources/template.html
git commit -m "feat: add 导出 PPTX toolbar button + downloadPPTX JS

POSTs serialized SVG to localhost:8765/export, downloads .pptx blob.
Graceful hints when server down or python-pptx missing.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: quality checker — require the PPTX button (TDD)

**Files:**
- Modify: `architecture-diagram/scripts/svg_quality_checker.py` (add check in `check_html_content`)
- Modify: `architecture-diagram/tests/test_svg_quality_checker.py` (update 2 existing tests + add 1 new)

**Step 1: Update the two existing passing tests to include the PPTX button**

In `architecture-diagram/tests/test_svg_quality_checker.py`:

In `test_html_template_with_expected_structure_passes`, change the toolbar block:
```python
      <button class="toolbar-btn" onclick="copyMermaid(this)">Mermaid</button>
      <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
      <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
```
to:
```python
      <button class="toolbar-btn" onclick="copyMermaid(this)">Mermaid</button>
      <button class="toolbar-btn" onclick="copySVG(this)">复制 SVG</button>
      <button class="toolbar-btn" onclick="downloadSVG(this)">下载 SVG</button>
      <button class="toolbar-btn" onclick="downloadPPTX(this)">导出 PPTX</button>
```
Do the identical edit in `test_mermaid_svg_label_mismatch_warns` (its toolbar block is the same 3-button snippet).

Run to confirm they still pass (check not added yet):
```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_svg_quality_checker.py
```
Expected: `OK` (existing tests still pass — button is present).

**Step 2: Write the failing test for the missing-button case**

Add this test method to `SVGQualityCheckerTests` in `architecture-diagram/tests/test_svg_quality_checker.py`:
```python
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
```

**Step 3: Run to verify the new test fails**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_svg_quality_checker.py
```
Expected: FAIL — `test_html_missing_pptx_button_fails` fails (`result["passed"]` is True because no check exists yet → `assertFalse(True)` fails).

**Step 4: Implement the check**

In `architecture-diagram/scripts/svg_quality_checker.py`, inside `check_html_content`, after the SVG copy/download check (after the line `result.errors.append("Missing SVG copy/download actions")`), add:
```python
        if "导出 PPTX" not in html or "downloadPPTX(" not in html:
            result.errors.append("Missing PPTX export action")
```

**Step 5: Run to verify all tests pass**

```bash
cd D:/architecture-diagram-generator
python architecture-diagram/tests/test_svg_quality_checker.py
```
Expected: `OK` (all tests pass, including the new missing-button test).

Also run the checker on the template itself to confirm it passes:
```bash
cd D:/architecture-diagram-generator/architecture-diagram
python scripts/svg_quality_checker.py resources/template.html
```
Expected: `PASS: resources/template.html` (template now has the PPTX button).

**Step 6: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/scripts/svg_quality_checker.py architecture-diagram/tests/test_svg_quality_checker.py
git commit -m "feat: quality checker requires the 导出 PPTX toolbar button

Hard error when downloadPPTX button/action missing from HTML templates,
parallel to the existing SVG/Mermaid button checks.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: SKILL.md — document the PPTX export feature

**Files:**
- Modify: `architecture-diagram/SKILL.md`

**Step 1: Update the toolbar table**

In `architecture-diagram/SKILL.md`, the 「导出工具栏」 table currently lists 3 buttons. Replace:
```markdown
| 按钮 | 功能 |
|------|------|
| Mermaid | 复制 Mermaid 源码到剪贴板 |
| 复制 SVG | 复制 SVG XML 到剪贴板 |
| 下载 SVG | 下载 .svg 文件 |
```
with:
```markdown
| 按钮 | 功能 |
|------|------|
| Mermaid | 复制 Mermaid 源码到剪贴板 |
| 复制 SVG | 复制 SVG XML 到剪贴板 |
| 下载 SVG | 下载 .svg 文件 |
| 导出 PPTX | 经本地服务转为原生可编辑 .pptx（需先启动服务，见下） |

模板中必须保留的元素：
- `id="report-container"` 在 `.container` 上
- `.toolbar` + `.toolbar-btn` 按钮（含 `downloadPPTX`）
- `@media print { .toolbar { display: none !important; } }`
- `copyMermaid()`, `copySVG()`, `downloadSVG()`, `downloadPPTX()` 函数
- 模板不得引入外部图片导出库
```

**Step 2: Add the 「PPTX 导出」 section**

Insert a new top-level section after 「导出工具栏」 (before 「组件方块模板」):
```markdown
## PPTX 导出（原生可编辑形状）

「导出 PPTX」按钮把当前 SVG 转成 **PowerPoint 原生形状**的 `.pptx`：圆角矩形、虚线边框、箭头都作为可编辑形状保留（PowerPoint 自带的「导入 SVG → 转换为形状」会丢圆角和虚线，不要走那条路）。

### 工作方式

浏览器无法直接运行 Python 转换器，因此通过一个本地小服务桥接：

1. 一次性启动本地服务（常驻）：
   ```bash
   pip install -r architecture-diagram/requirements.txt   # 仅首次，装 python-pptx
   python architecture-diagram/scripts/pptx_server.py
   ```
   服务监听 `http://localhost:8765`。
2. 在浏览器中打开任意生成的 `.html`，点「导出 PPTX」→ 下载 `diagram.pptx`。
3. 服务没启动时按钮回显「✗ 先起服务」；未装 python-pptx 时回显「✗ 装依赖」。

也可以用 CLI 直接转单文件：
```bash
python architecture-diagram/scripts/export_pptx.py diagram.svg -o diagram.pptx
```

### 保真映射

| SVG | PPTX 原生形状 |
|-----|---------------|
| `<rect rx>` | `roundRect`（带可拖拽圆角手柄） |
| `stroke-dasharray` | `prstDash` / `custDash`（虚线保留） |
| `<marker>` 箭头 | `tailEnd type="triangle"` |
| `#hex` 颜色 | `srgbClr` |
| `opacity`/`fill-opacity`/`stroke-opacity` | `alpha` |

### 已知限制

- **`rgba()` 颜色不解析**：转换器只认 `#hex`，使用 `rgba()` 的元素在 PPTX 中会失去填充/描边。SVG 配色请优先用 `#hex`（半透明用 `#hex` + `stroke-opacity`/`fill-opacity`，或预计算浅色 hex）。示例 SVG 已全程用 hex。
- 网格底纹 `<pattern>` 在 PPTX 中不渲染（装饰性，可接受）。
- 不含动画、旁白、笔记、图片媒体。

### 验证

下载 PPTX → 在 PowerPoint 打开 → 确认：圆角在、虚线在、箭头在、颜色一致、文字可读、每个形状可单独选中编辑。
```

**Step 3: Update the 「PowerPoint 兼容性」 section**

In the existing 「PowerPoint 兼容性」 section (near the end of SKILL.md), change the framing so SVG-import is no longer the recommended path for editable shapes. After the existing numbered list, add:
```markdown
> **要可编辑形状（圆角/虚线/箭头原生保留）**：用「导出 PPTX」按钮或 `export_pptx.py` 生成原生 PPTX（见「PPTX 导出」小节）。
> **SVG 导入 PowerPoint + 转换为形状** 是有损的，仅适用于网页预览或作为图片使用。
```

**Step 4: Add an acceptance step to 「验收检查」**

In the 「验收检查」 numbered list, after step 6 (PowerPoint 目视确认), add:
```markdown
7. （可选）启动 `pptx_server.py` 后点「导出 PPTX」→ 在 PowerPoint 打开 → 确认圆角、虚线、箭头保留且形状可编辑
```

**Step 5: Commit**

```bash
cd D:/architecture-diagram-generator
git add architecture-diagram/SKILL.md
git commit -m "docs: document PPTX export feature in SKILL.md

New PPTX 导出 section (server bridge + CLI + fidelity mapping + rgba
limitation); toolbar table → 4 buttons; PowerPoint compatibility section
now steers editable-shape use to PPTX export; acceptance step added.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Manual acceptance

**Files:** none (verification only)

**Step 1: Generate a test diagram with the full vocabulary**

Using the skill, generate an architecture diagram HTML that includes: rounded component rects (`rx`), a dashed area boundary (`stroke-dasharray`), and at least one arrow (`<marker>` + `<line>`/`<path>`). Save as `examples/test-pptx.html`.

**Step 2: Run the quality checker**

```bash
cd D:/architecture-diagram-generator/architecture-diagram
python scripts/svg_quality_checker.py examples/test-pptx.html
```
Expected: `PASS`.

**Step 3: Start the server and export**

```bash
python scripts/pptx_server.py &
# (in browser) open examples/test-pptx.html, click 导出 PPTX
```
Expected: browser downloads `diagram.pptx`; button shows "✓ 完成".

**Step 4: Open in PowerPoint and verify**

Open `diagram.pptx` in PowerPoint. Confirm:
- [ ] Rounded rects have rounded corners (with draggable yellow handles)
- [ ] Dashed area boundary is dashed
- [ ] Arrows have arrowheads
- [ ] Colors match the HTML preview
- [ ] Text is readable and positioned sensibly
- [ ] Each shape is individually selectable / editable (not a flat image)
- [ ] No "repair" prompt on open

If text is visibly misaligned, note the offset for a future v1.1 baseline-compensation tweak (the converter uses `box_y = y - fontSize×0.85`; acceptable minor drift is expected).

**Step 5: Run the full test suite**

```bash
cd D:/architecture-diagram-generator/architecture-diagram
python -m unittest discover -s tests -p "test_*.py" -v
```
Expected: all tests pass (svg_quality_checker + export_pptx + pptx_server).

---

## Notes for the implementer

- **Branch:** `feat/pptx-export` (already created; the design doc is committed there).
- **No external JS libs:** the browser button uses only `fetch` + `Blob`; the template stays self-contained. The PPTX path is the only thing requiring the local Python server.
- **`tspan_flattener.py` is a stub by design** — do not copy ppt-master's real one (it pulls in the `svg_finalize` package). See the file's docstring.
- **`use_expander.py` is vendored but dead** (the `icons_dir` guard never triggers here) — kept only as cheap insurance so the vendored converter stays byte-identical to ppt-master's.
- **rgba is intentionally NOT migrated this round** — documented as a known limitation. If a generated diagram uses `rgba()`, those elements lose fill in the PPTX. Use `#hex` + opacity attrs instead.
- **Frequent commits** — one commit per task as shown.
