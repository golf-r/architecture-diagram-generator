#!/usr/bin/env python3
"""Quality checks for architecture diagram HTML/SVG outputs.

The checker accepts either a self-contained HTML template or a standalone SVG.
For HTML inputs it extracts the first <svg> block and verifies that the page
still contains the expected toolbar and Mermaid source.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET


SVG_TAG_RE = re.compile(r"<svg\b.*?</svg>", re.IGNORECASE | re.DOTALL)


class QualityResult:
    def __init__(self, path: str, passed: bool = True):
        self.path = path
        self.passed = passed
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def __getitem__(self, key: str):
        return getattr(self, key)


class SVGQualityChecker:
    """Validate HTML templates or raw SVG diagrams."""

    def check_file(self, path: str | Path) -> QualityResult:
        input_path = Path(path)
        content = input_path.read_text(encoding="utf-8")
        suffix = input_path.suffix.lower()

        if suffix == ".html" or suffix == ".htm":
            return self.check_html_content(content, source_path=input_path)
        return self.check_svg_content(content, source_path=input_path)

    def check_html_content(self, html: str, source_path: str | Path | None = None) -> QualityResult:
        result = QualityResult(path=str(source_path) if source_path else "<html>")

        if 'class="toolbar"' not in html and "class='toolbar'" not in html:
            result.errors.append("Missing toolbar container")
        if "copyMermaid(" not in html:
            result.errors.append("Missing Mermaid copy action")
        if "复制 SVG" not in html or "downloadSVG(" not in html:
            result.errors.append("Missing SVG copy/download actions")
        if "导出 PPTX" not in html or "downloadPPTX(" not in html:
            result.errors.append("Missing PPTX export action")
        if 'class="mermaid-src"' not in html and "class='mermaid-src'" not in html:
            result.errors.append("Missing hidden Mermaid source block")

        svg_match = SVG_TAG_RE.search(html)
        if not svg_match:
            result.errors.append("Missing <svg> block")
            result.passed = False
            return result

        svg_result = self.check_svg_content(
            svg_match.group(0),
            source_path=source_path,
            html_content=html,
        )
        result.errors.extend(svg_result.errors)
        result.warnings.extend(svg_result.warnings)
        result.info.extend(svg_result.info)
        result.passed = len(result.errors) == 0
        return result

    def check_svg_content(
        self,
        svg: str,
        source_path: str | Path | None = None,
        html_content: str | None = None,
    ) -> QualityResult:
        result = QualityResult(path=str(source_path) if source_path else "<svg>")

        try:
            root = ET.fromstring(svg)
        except ET.ParseError as exc:
            result.errors.append(f"Invalid SVG XML: {exc}")
            result.passed = False
            return result

        if self._strip_ns(root.tag) != "svg":
            result.errors.append("Root element is not <svg>")

        viewbox = root.attrib.get("viewBox")
        if not viewbox:
            result.errors.append("Missing viewBox attribute")
        elif not re.match(r"^0 0 \d+ \d+$", viewbox):
            result.warnings.append(f"Unusual viewBox format: {viewbox}")

        width = root.attrib.get("width")
        height = root.attrib.get("height")
        if width and height and viewbox:
            parts = viewbox.split()
            if len(parts) == 4 and (width != parts[2] or height != parts[3]):
                result.warnings.append(
                    f"Width/height do not match viewBox: width={width} height={height} viewBox={viewbox}"
                )

        if not root.attrib.get("role"):
            result.warnings.append("Missing role attribute")
        if not root.attrib.get("aria-label"):
            result.warnings.append("Missing aria-label attribute")

        self._check_text_overflow(svg, root, result)
        self._check_arrow_crossing(svg, root, result)
        self._check_arrow_endpoint_distance(root, result)
        self._check_unused_defs(svg, root, result)
        self._check_layout_spacing_and_placement(root, result)

        if re.search(r"<script\b", svg, re.IGNORECASE):
            result.errors.append("Detected forbidden <script> element")
        if re.search(r"<foreignObject\b", svg, re.IGNORECASE):
            result.errors.append("Detected forbidden <foreignObject> element")
        if re.search(r"\bclass\s*=", svg):
            result.errors.append("Detected forbidden class attribute")
        if re.search(r"<style\b", svg, re.IGNORECASE):
            result.errors.append("Detected forbidden <style> element")

        if html_content is not None:
            self._check_mermaid_consistency(html_content, root, result)

        result.passed = len(result.errors) == 0
        return result

    def _check_text_overflow(self, svg: str, root: ET.Element, result: QualityResult) -> None:
        text_nodes = list(root.iter())
        for node in text_nodes:
            if self._strip_ns(node.tag) != "text":
                continue
            text = "".join(node.itertext()).strip()
            if len(text) > 32:
                result.warnings.append(f"Possible text overflow risk: {text}")

    def _check_arrow_crossing(self, svg: str, root: ET.Element, result: QualityResult) -> None:
        rects = self._collect_rects(root)
        for line in root.iter():
            tag = self._strip_ns(line.tag)
            if tag not in {"line", "path"}:
                continue
            segments = self._extract_segments(line)
            for x1, y1, x2, y2 in segments:
                for rect in rects:
                    if self._segment_crosses_rect(x1, y1, x2, y2, rect):
                        result.errors.append("Detected arrow segment crossing a component rectangle")
                        return

    def _check_arrow_endpoint_distance(self, root: ET.Element, result: QualityResult) -> None:
        rects = self._collect_rects(root)
        for node in root.iter():
            if self._strip_ns(node.tag) != "line":
                continue
            x2 = float(node.attrib.get("x2", "0"))
            y2 = float(node.attrib.get("y2", "0"))
            for left, top, right, bottom in rects:
                if top <= y2 <= bottom:
                    distance = min(abs(left - x2), abs(right - x2))
                    if distance <= 2:
                        result.warnings.append(f"Arrow endpoint distance is too small: {distance}px")
                    elif distance > 12:
                        result.warnings.append(f"Arrow endpoint distance is too large: {distance}px")
                    break

    def _check_unused_defs(self, svg: str, root: ET.Element, result: QualityResult) -> None:
        marker_ids = set(re.findall(r'<marker[^>]*id="([^"]+)"', svg, re.IGNORECASE))
        marker_ids.update(re.findall(r"<marker[^>]*id='([^']+)'", svg, re.IGNORECASE))
        if not marker_ids:
            return
        used_marker_ids = set(re.findall(r'marker-end="url\(#([^)]+)\)"', svg, re.IGNORECASE))
        used_marker_ids.update(re.findall(r"marker-end='url\(#([^)]+)\)'", svg, re.IGNORECASE))
        unused = sorted(marker_ids - used_marker_ids)
        if unused:
            result.warnings.append("Unused marker/defs entries: " + ", ".join(unused))

    def _check_layout_spacing_and_placement(self, root: ET.Element, result: QualityResult) -> None:
        rects = self._collect_rects(root)
        for i, rect_a in enumerate(rects):
            for rect_b in rects[i + 1:]:
                gap = self._rect_gap(rect_a, rect_b)
                if gap < 20:
                    result.warnings.append(f"Layout spacing is too tight: {gap}px")

        texts = []
        for node in root.iter():
            if self._strip_ns(node.tag) != "text":
                continue
            text = "".join(node.itertext()).strip()
            if not text:
                continue
            x = float(node.attrib.get("x", "0"))
            y = float(node.attrib.get("y", "0"))
            texts.append((text, x, y))

        for text, x, y in texts:
            if self._looks_like_title(text) and y > 80:
                result.warnings.append(f"Title placement is too low: {text}")
            if self._looks_like_legend(text) and (x > 120 or y > 80):
                result.warnings.append(f"Legend placement is too far from the top-left: {text}")
            elif self._looks_like_legend(text) and (x <= 120 and y <= 80):
                result.warnings.append(f"Legend placement is in the top-left content area: {text}")
            if self._looks_like_annotation(text) and (x > 60 and y > 60):
                result.warnings.append(f"Annotation placement is inside the main content area: {text}")

    @staticmethod
    def _rect_gap(rect_a, rect_b) -> float:
        left_a, top_a, right_a, bottom_a = rect_a
        left_b, top_b, right_b, bottom_b = rect_b
        horizontal_gap = max(0.0, max(left_b - right_a, left_a - right_b))
        vertical_gap = max(0.0, max(top_b - bottom_a, top_a - bottom_b))
        if horizontal_gap and vertical_gap:
            return min(horizontal_gap, vertical_gap)
        return max(horizontal_gap, vertical_gap)

    @staticmethod
    def _looks_like_title(text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["架构图", "flowchart", "diagram", "title", "标题"])

    @staticmethod
    def _looks_like_legend(text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["legend", "图例"])

    @staticmethod
    def _looks_like_annotation(text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["注释", "说明", "备注", "note", "annotation"])

    def _check_mermaid_consistency(self, html: str, root: ET.Element, result: QualityResult) -> None:
        mermaid = self._extract_mermaid_text(html)
        if not mermaid:
            return

        mermaid_labels = [m.strip() for m in re.findall(r"\[(?:([^\]]+))\]", mermaid)]
        svg_texts = ["".join(node.itertext()).strip() for node in root.iter() if self._strip_ns(node.tag) == "text"]

        if mermaid_labels and svg_texts:
            missing = [label for label in mermaid_labels if not any(label in text for text in svg_texts)]
            if missing:
                result.warnings.append(
                    "Mermaid and SVG labels may be inconsistent: " + ", ".join(missing)
                )

    @staticmethod
    def _extract_mermaid_text(html: str) -> str:
        match = re.search(r'<pre[^>]*class="mermaid-src"[^>]*>(.*?)</pre>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        match = re.search(r"<pre[^>]*class='mermaid-src'[^>]*>(.*?)</pre>", html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return ""

    @staticmethod
    def _collect_rects(root: ET.Element):
        rects = []
        for node in root.iter():
            if node.tag.endswith("rect"):
                if "stroke-dasharray" in node.attrib or "opacity" in node.attrib:
                    continue
                w_str = node.attrib.get("width", "0")
                h_str = node.attrib.get("height", "0")
                w = float(w_str) if w_str.replace(".", "").isdigit() else 0
                h = float(h_str) if h_str.replace(".", "").isdigit() else 0
                if w == 0 and h == 0:
                    continue
                x = float(node.attrib.get("x", "0"))
                y = float(node.attrib.get("y", "0"))
                rects.append((x, y, x + w, y + h))
        return rects

    @staticmethod
    def _segment_crosses_rect(x1: float, y1: float, x2: float, y2: float, rect) -> bool:
        left, top, right, bottom = rect
        if x1 == x2:
            if left < x1 < right:
                seg_top, seg_bottom = sorted((y1, y2))
                return seg_top < bottom and seg_bottom > top
            return False
        if y1 == y2:
            if top < y1 < bottom:
                seg_left, seg_right = sorted((x1, x2))
                return seg_left < right and seg_right > left
            return False
        return False

    @staticmethod
    def _extract_segments(node: ET.Element):
        tag = SVGQualityChecker._strip_ns(node.tag)
        if tag == "line":
            return [(
                float(node.attrib.get("x1", "0")),
                float(node.attrib.get("y1", "0")),
                float(node.attrib.get("x2", "0")),
                float(node.attrib.get("y2", "0")),
            )]
        if tag == "path":
            d = node.attrib.get("d", "")
            points = re.findall(r"([ML])\s*([\d.]+)\s*([\d.]+)", d, re.IGNORECASE)
            if len(points) < 2:
                return []
            segments = []
            prev = None
            for _, x, y in points:
                current = (float(x), float(y))
                if prev is not None:
                    segments.append((prev[0], prev[1], current[0], current[1]))
                prev = current
            return segments
        return []

    @staticmethod
    def _strip_ns(tag: str) -> str:
        if tag.startswith("{"):
            return tag.split("}", 1)[1]
        return tag


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate architecture diagram HTML/SVG quality")
    parser.add_argument("path", help="HTML or SVG file to check")
    parser.add_argument("--publish", action="store_true", help="Treat warnings as errors for final release checks")
    args = parser.parse_args(argv)

    checker = SVGQualityChecker()
    result = checker.check_file(args.path)

    for message in result.info:
        print(f"INFO: {message}")
    for message in result.warnings:
        print(f"WARNING: {message}")
    for message in result.errors:
        print(f"ERROR: {message}")

    if args.publish and result.warnings:
        result.errors.append("Publish mode treats warnings as errors")
        result.passed = False

    if result.passed:
        print(f"PASS: {result.path}")
        return 0
    print(f"FAIL: {result.path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
