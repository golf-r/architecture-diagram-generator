# Third-Party Notices: svg_to_pptx

The Python files in this directory (`drawingml_context.py`,
`drawingml_utils.py`, `drawingml_paths.py`, `drawingml_styles.py`,
`drawingml_elements.py`, `drawingml_converter.py`, `use_expander.py`)
are vendored verbatim from the **ppt-master** skill
(Cocoon AI, MIT License - same copyright holder as this repository;
see the repo-root `LICENSE`).

- **Source:** the `ppt-master` skill package, `scripts/svg_to_pptx/`
  (installed at `~/.claude/skills/ppt-master/scripts/svg_to_pptx/`).
- **Vendored:** 2026-08-03 (consuming commit `84f4277` on `feat/pptx-export`).
- **Not vendored** (intentionally trimmed): `pptx_builder.py`, `pptx_cli.py`,
  `pptx_media.py`, `pptx_notes.py`, `pptx_narration.py`, `animation_config.py`,
  `pptx_slide_xml.py`, `pptx_dimensions.py`, `pptx_discovery.py`, and the
  real `tspan_flattener.py` (which depends on ppt-master's `svg_finalize`
  package). `tspan_flattener.py` here is a local no-op stub; `__init__.py`
  is a local trimmed wrapper.

## To update

1. Re-copy the seven files above from a current ppt-master install.
2. Keep the local `tspan_flattener.py` stub and trimmed `__init__.py`
   (do not overwrite them with ppt-master's versions).
3. From `architecture-diagram/`, re-run:
   `python -c "import sys; sys.path.insert(0,'scripts'); from svg_to_pptx import convert_svg_to_slide_shapes; print('import ok')"`
4. Update the "Vendored" date/commit above.
