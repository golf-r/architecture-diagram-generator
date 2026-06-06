---
name: architecture-diagram
description: Use when creating architecture overview diagrams or flowcharts that need Mermaid source, HTML preview, and premium SVG output with Chinese UI and a white background.
---

# Architecture Diagram Skill

Create professional architecture overview diagrams and flowcharts as self-contained HTML files with inline SVG graphics and CSS styling — white background, Chinese UI, clean, minimal, and visually premium. The default workflow is: preview in HTML, copy Mermaid source, then export SVG.

> **Version 2.0** · MIT License · Adapted from Cocoon AI

## Design System

### Diagram Quality Requirements

- Logic must be self-consistent. Every component, arrow, and label should reflect the actual system boundary or data flow.
- Prefer low-saturation fills with stronger strokes. Avoid neon colors, pure black borders, and overly bright reds.
- Do not allow arrows or connector lines to overlap boxes, labels, or each other unless there is no cleaner alternative and the route is clearly separated.
- If a clean route is not possible, rearrange the layout first. Do not force a crossing line.
- Use orthogonal or L-shaped routing by default; use a straight line only when it is clearly unobstructed.
- Keep arrow labels short and place them away from corners, boundaries, and other labels.
- The final diagram should read cleanly at a glance, without visual congestion.

### Color Palette (OKLCH)

Use OKLCH color space. Reduce chroma as lightness approaches 0 or 100. Never use `#000` or `#fff` — tint every neutral toward the brand hue (chroma 0.005–0.01). Default brand hue: 250° (blue-cyan).

Semantic colors for component types on **white background**:

| Component Type | Fill (oklch) | Stroke (oklch) |
|---------------|--------------|-----------------|
| Frontend / Entry | `oklch(0.92 0.04 250 / 0.12)` | `oklch(0.55 0.2 250)` |
| Backend / Core | `oklch(0.92 0.035 170 / 0.12)` | `oklch(0.55 0.17 170)` |
| Database / Storage | `oklch(0.9 0.05 300 / 0.12)` | `oklch(0.5 0.2 300)` |
| Cloud / External API | `oklch(0.92 0.04 230 / 0.12)` | `oklch(0.55 0.18 230)` |
| Security | `oklch(0.92 0.06 20 / 0.12)` | `oklch(0.55 0.22 20)` |
| Plugin / Message Bus | `oklch(0.92 0.04 80 / 0.12)` | `oklch(0.55 0.18 80)` |
| External/Generic | `oklch(0.92 0.01 260 / 0.12)` | `oklch(0.55 0.03 260)` |

Neutral colors (page, text, borders):

| Element | OKLCH |
|---------|-------|
| Page background | `#ffffff` |
| Card background | `#ffffff` |
| Primary text | `oklch(0.18 0.015 260)` |
| Muted text | `oklch(0.55 0.02 260)` |
| Annotation text | `oklch(0.55 0.025 260)` |
| Border / divider | `oklch(0.9 0.008 260)` |
| Arrow stroke | `oklch(0.62 0.025 260)` |
| Button hover | `oklch(0.96 0.006 260)` |

### Typography

Use Microsoft YaHei for Chinese readability:
```html
font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif;
```

Hierarchy through weight + size contrast (≥1.25 ratio between steps):

| Element | Size | Weight |
|---------|------|--------|
| Title | 18px | 650 |
| Subtitle | 13px | 420 |
| Component name | 12–13px | 620–650 |
| Sublabel | 9–10px | 400 |
| Annotation / arrow label | 9px | 500 |
| Layer pill label | 10px | 600 |

### Visual Elements

**Background:** Tinted light page with white card container:
```css
body { background: #ffffff; }
.container { background: #ffffff; box-shadow: 0 1px 2px oklch(0 0 0 / 0.04), 0 8px 24px oklch(0 0 0 / 0.06); }
```

**Pulse dot:** Animated indicator in header:
```css
.pulse-dot { width: 10px; height: 10px; border-radius: 50%; background: oklch(0.55 0.2 250); animation: pulse 2.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.85); } }
```

**Grid pattern:** Very light on white background:
```svg
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
  <path d="M 32 0 L 0 0 0 32" fill="none" stroke="oklch(0.96 0.006 250)" stroke-width="0.5"/>
</pattern>
```

**Layer labels:** Use filled pill rect + white text instead of bare label text:
```svg
<rect x="X" y="Y" width="84" height="20" rx="4" fill="STROKE_COLOR" />
<text x="CX" y="Y+14" fill="oklch(1 0.005 250)" font-size="10" font-weight="600" text-anchor="middle">层名称</text>
```

**Component boxes:** Rounded rectangles (`rx="6"`–`"7"`) with 1.3–1.5px stroke, light translucent fills. No opaque background needed (fills are transparent enough on white).

**Region boundaries:** Dashed stroke (`stroke-dasharray="5,3"`), matching component color, with subtle tinted fill (`/ 0.08`).

**Arrows:** Use SVG markers for arrowheads, drawn before component boxes (behind them):
```svg
<marker id="a-gray" markerWidth="8" markerHeight="5.5" refX="7" refY="2.75" orient="auto">
  <polygon points="0 0, 8 2.75, 0 5.5" fill="oklch(0.62 0.025 260)" />
</marker>
```

**Routing rule:** Prefer orthogonal segments and spacer gaps over diagonal shortcuts. If two routes would cross, move one component or split the layer into a separate row.

**Arrow labels:** White rounded pill (`rx="3"`) behind text for legibility over grid lines:
```html
<rect x="X" y="Y" width="W" height="15" rx="3" fill="oklch(1 0.005 250)" opacity="0.88" />
<text x="X+3" y="Y+11" fill="oklch(0.55 0.025 260)" font-size="9" font-weight="500">标签</text>
```

### Layout Rules

- **Component height:** 55px for services, 60-85px for larger groups
- **Minimum horizontal gap between sibling components:** 30px
- **Minimum vertical gap between stacked components:** 40px
- **Layer boundary padding (from outermost components):** 15-20px on each side
- **Legend offset from lowest element:** ≥15px
- **Arrow end offset from target:** 2px (for marker-end rendering)
- **Arrow label position:** centered between connected edges, ±8px from arrow line

### Premium Styling Rules

- Use OKLCH fills at 8%-15% lightness + low chroma, and consistent mid-chroma strokes.
- Use `oklch(0.18 0.015 260)` for primary text, `oklch(0.55 0.02 260)` for annotations/descriptions.
- Prefer spacious layouts with fewer but clearer arrows over dense connector webs.
- Use dashed boundaries only for regions with subtle tinted fills; keep them subtle.
- Arrow labels get a semi-transparent white pill background (`opacity="0.88"`) for legibility over grid lines.
- Maintain 650/420/620/400 font weight contrast between title, subtitle, component names, and sub-labels.
- Use `rx="5"`–`"7"` rounded corners consistently throughout; don't mix corner radii.

### Legend Placement

- Place legend at least 15px below the lowest boundary/component
- Expand SVG viewBox height if needed

### Layout Structure

1. **Header** — Title with pulsing dot indicator and export toolbar
2. **Main SVG diagram** — Contained in rounded border card
3. **No summary cards or footer** — keep output clean and minimal

## Common Diagram Types

- **Architecture overview diagrams**: Show system boundaries, major components, and data flow at a high level.
- **Flowcharts**: Show step-by-step process logic, decisions, and branches.

## Export Policy

- Mermaid is the editable source.
- SVG is the shareable vector format.
- Keep the HTML preview self-contained so the diagram can be reviewed before export.

### Export Toolbar (built-in)

Every diagram ships with a header toolbar containing three buttons — Mermaid, Copy SVG, and Download SVG.

Minimal JavaScript is allowed for toolbar actions only. The diagram itself must remain SVG-first and self-contained.

Keep these intact in the template:
- `id="report-container"` on the outermost `.container` div
- `.toolbar` div with `.toolbar-btn` buttons
- `@media print { .toolbar { display: none !important; } }`
- `copyMermaid()`, `copySVG()`, `downloadSVG()` before `</body>`
- The template should remain free of external image export libraries

### Component Box Pattern

```svg
<rect x="X" y="Y" width="W" height="H" rx="7" fill="oklch(HUE_CHROMA / 0.12)" stroke="STROKE_OKLCH" stroke-width="1.3"/>
<text x="CX" y="Y+22" fill="oklch(0.18 0.015 260)" font-size="12" font-weight="620" text-anchor="middle">NAME</text>
<text x="CX" y="Y+38" fill="oklch(0.55 0.02 260)" font-size="9" text-anchor="middle">说明文字</text>
```

## Template

Copy and customize the template at `resources/template.html`. Key customization points:

1. Update the `<title>` and header text (Chinese)
2. Modify SVG viewBox dimensions
3. Add/remove/reposition component boxes
4. Draw connection arrows between components
5. Update legend colors

## Arrow Routing Reference

Creating complex architecture overview diagrams with multiple layers and crossing arrows requires careful coordinate planning. For reusable routing patterns, see `resources/routing.js`:

- **L-shape:** Vertical then horizontal (component in different rows/columns)
- **U-shape:** Route around an obstacle by going wide and then back in
- **Obstacle avoidance:** Pass through narrow gaps between side-by-side components

### Boundary Detection Checklist

After placing all component boxes and before drawing arrows, verify:

```
[ ] No two component rects overlap (check x-range vs x-range, y-range vs y-range)
[ ] Arrow endpoints are 2px from target component edge
[ ] Each arrow's intermediate segments avoid all component rects
    (check every segment's y against every rect's y-range,
     and every segment's x against every rect's x-range)
[ ] Arrow labels do not overlap any rect
[ ] No two arrows cross at the same point (parallel lines OK, crossing X-shape is not)
[ ] Layer boundaries are ≥15px beyond outermost component edges
[ ] Legend is ≥15px below lowest boundary/component
[ ] viewBox height accommodates everything with 10-20px bottom padding
```

### Verification Gate

**Before claiming the diagram is complete, run this checklist:**

1. Open the `.html` file in a browser
2. Visually confirm: no arrows pass through boxes
3. Visually confirm: all labels legible
4. Run the quality checker on the HTML preview and the exported SVG
5. Toggle the export toolbar and test Mermaid, copy SVG, and download SVG
6. If any issue found → fix coordinates or markup and re-run from step 1

### Quality Check Workflow

Run the checker before shipping any diagram output:

```bash
python scripts/svg_quality_checker.py path/to/diagram.html
python scripts/svg_quality_checker.py path/to/diagram.svg
python scripts/svg_quality_checker.py --publish path/to/diagram.html
python scripts/svg_quality_checker.py --publish path/to/diagram.svg
```

The checker must treat these as hard errors:

- invalid SVG XML
- missing `viewBox`
- missing `toolbar` / `mermaid-src` in the HTML wrapper
- missing Mermaid / SVG toolbar actions in the HTML wrapper
- forbidden SVG elements such as `script`, `foreignObject`, or `style`

The checker should surface these as warnings:

- missing `role="img"`
- missing `aria-label`
- unusual `viewBox` formatting
- width / height values that do not match the `viewBox`

For final release / sharing / export, run the checker with `--publish` so any warning also fails the check. Use the non-publish mode only for iteration while you are still arranging the diagram.

**Red flags — stop and verify:**
- "Arrows look right in my head" → open the file and look
- "The coordinates should work" → calculate, don't estimate
- "Close enough" → overlapping arrow is a visual bug, not "close enough"

## Mermaid 导出

架构图和流程图都以 Mermaid 作为可编辑源定义，HTML 负责预览，SVG 负责对外分享。

### 使用方式

生成 HTML 后，使用工具栏复制 Mermaid 源码；需要分享或归档时，导出 SVG。

### SVG → Mermaid 映射规则

| SVG 元素 | Mermaid | 说明 |
|---------|---------|------|
| 入口组件 | `A([text])` | 跑道圆角，cyan 色 |
| 核心服务 | `A[text]` | 直角矩形，emerald 色 |
| 插件/采集器 | `A[text]` + `subgraph` | 矩形含子节点，orange 色 |
| 存储/数据库 | `A[(text)]` | 圆柱形，violet 色 |
| 外部 API | `A([text])` | 跑道圆角，amber 色 |
| 层边界 | `subgraph 名称 ... end` | 对应 SVG 虚线矩形 |
| 箭头 | `-->` / `--\|标签\|-->` | 与 SVG 箭头对应 |
| 组件说明行 | `A[名称<br/>说明]` | `<br/>` 在 Mermaid 节点内换行 |
| 图方向 | `flowchart TD` / `flowchart LR` | 自上而下 / 自左向右；子图内加 `direction LR` 实现层内横向排列 |

### 完整示例

对一个三层架构（入口 → 核心 → 外部），Mermaid 定义如下：

```
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4f8', 'primaryBorderColor': '#2b95c2', 'lineColor': '#94a3b8', 'fontFamily': 'Microsoft YaHei'}}}%%
flowchart TD
  subgraph 核心层
    direction LR
    M[main.py<br/>程序入口 · 流程编排]
    PM[PluginManager<br/>动态加载 · 生命周期]
  end
  subgraph 插件层
    direction LR
    CP[采集器插件<br/>issue · pr · commit]
  end
  subgraph 外部
    direction LR
    API[(GitCode API)]
  end
  M --> PM
  PM --> CP
  CP --> API
```

### 注意事项

- Mermaid `themeVariables` 对所有节点应用同一颜色。如需多层多色（如核心层 emerald + 插件层 orange），可使用 `classDef` 为不同 `subgraph` 内的节点单独赋色
- 复杂绕行箭头在 Mermaid 中简化为直接连线（Mermaid 自动布局处理）
- 子组件（如采集器内的 GitHub/Gitee 等）在 Mermaid 中简化为单节点
- 默认使用 `flowchart TD` + 子图内 `direction LR`（层间纵向、层内横向），也可整体切换为 `flowchart LR`（全横向）
- 如果 Mermaid 自动布局导致线条交叉，优先调整子图顺序、拆分层次或加入中间汇聚节点，而不是接受交叉。

### 自检

```
[ ] Mermaid 定义语法正确（%%{init}%% 块闭合、括号匹配、箭头方向正确）
[ ] 与 SVG 图内容一致（节点、层级、连接关系匹配）
[ ] 在浏览器中预览正常，SVG 导出后仍保持清晰矢量效果
[ ] `python scripts/svg_quality_checker.py path/to/diagram.html` 无错误
[ ] `python scripts/svg_quality_checker.py path/to/diagram.svg` 无错误
```

## Output

Always produce a single self-contained `.html` file with:
- Embedded CSS (inline styles)
- Inline SVG (no external images)
- Pure SVG for the diagram itself; tiny JavaScript is allowed only for the export toolbar and Mermaid copy actions
- Export toolbar actions: Mermaid, Copy SVG, Download SVG
