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
