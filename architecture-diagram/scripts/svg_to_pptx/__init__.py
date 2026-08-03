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
