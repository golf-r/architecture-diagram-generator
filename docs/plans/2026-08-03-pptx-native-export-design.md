# 设计:为 architecture-diagram skill 新增 PPTX 导出(原生可编辑形状)

- 日期:2026-08-03
- 状态:已批准
- 作者:brainstorming 会话

## 背景与问题

architecture-diagram skill 生成的 SVG 导入 PowerPoint 后,「右键转换为形状」会丢失样式:

- 虚线区域边框(`stroke-dasharray`)变实线或丢失
- 圆角矩形(`<rect rx>`)变直角矩形

**根因**:PowerPoint 的「SVG -> 形状」转换器是有损的,只支持 SVG 的一个子集;`stroke-dasharray` 与 `rx` 不在其可靠支持范围内,且该子集无官方文档、随 PPT 版本变化。ppt-master 的 SKILL.md 第 528 行亦明确指出「PowerPoint's internal SVG parser drops icons and rounded corners」。

**目标**:导出的 PPTX 中,圆角 / 虚线 / 箭头作为**原生 DrawingML 形状**保留,且可在 PowerPoint 中单独选中编辑。

## 决策

复用 ppt-master 的 Python SVG -> DrawingML 转换器,**将核心代码 vendoring 到 architecture-diagram skill 下**(保持 skill 自包含,不依赖 ppt-master 已安装)。新增浏览器「导出 PPTX」按钮,通过本地小服务桥接浏览器与 Python 转换器。

## 架构

### Vendoring 范围

从 `ppt-master/scripts/svg_to_pptx/` 拷入 `architecture-diagram/scripts/svg_to_pptx/`,仅保留自包含、纯标准库的转换核心(已核对 import,只互相引用 + 标准库):

| 文件 | 作用 |
|------|------|
| `drawingml_context.py` | ConvertContext 数据结构 |
| `drawingml_utils.py` | EMU / 颜色 / 字体 / dash 预设工具 |
| `drawingml_paths.py` | `<path>` -> custGeom(含弧线转三次贝塞尔) |
| `drawingml_styles.py` | dash / marker / 颜色 / 效果 |
| `drawingml_elements.py` | rect->roundRect / text / line 元素映射 |
| `drawingml_converter.py` | `convert_svg_to_slide_shapes()` 编排器 |
| `use_expander.py`、`tspan_flattener.py` | 标准库小工具 |

**不拷(裁掉动画与旁白)**:`pptx_builder.py`、`pptx_cli.py`、`pptx_media.py`、`pptx_notes.py`、`pptx_narration.py`、`animation_config.py`、`pptx_animations.py`、`pptx_slide_xml.py`、`pptx_dimensions.py`、`pptx_discovery.py`。转换器核心 `drawingml_*` 不 import 这些,裁剪干净。

### 自写薄包装 `scripts/export_pptx.py`(~100-120 行)

核心函数 `convert_svg_to_pptx(svg_path, out_path)`,供 CLI 与本地服务共用:

1. 接受 `.svg`(或 `.html`,抽出内联 `<svg>`)。
2. 读 viewBox 算幻灯片尺寸(viewBox × 9525 EMU)。
3. 用 `python-pptx` 建空壳单页 PPTX(空白版式 `layouts[6]`),存临时 `base.pptx`。
4. 解包,调 `convert_svg_to_slide_shapes(svg_path, slide_num=1)` 得 slide1.xml,覆盖 `ppt/slides/slide1.xml`。
5. 重新打包成 `.pptx`。
6. 预处理:若转换器要求 tspan 预扁平化,先跑 `tspan_flattener`;若 `width="100%"` / `url(#grid)` 网格底纹导致转换出错,传入前剥掉(纯装饰)。

CLI 入口:`python scripts/export_pptx.py diagram.svg -o diagram.pptx`。

### 本地服务 `scripts/pptx_server.py`(~80 行,标准库 `http.server`)

桥接浏览器按钮与 Python 转换器:

- 监听 `localhost:8765`。
- `GET /health` -> 探测用。
- `POST /export`(body = SVG XML)-> 调 `convert_svg_to_pptx` -> 返回 `.pptx` blob。
- 发送 CORS 头(`Access-Control-Allow-Origin: *` 等),处理 OPTIONS 预检,供 `file://` 打开的 HTML 调用。
- 不引 Flask,仅标准库。

### 浏览器按钮 `resources/template.html`

工具栏新增第 4 个按钮「导出 PPTX」,`downloadPPTX(btn)`:

1. `fetch('http://localhost:8765/health')` 探测;失败回显「请先运行 `python scripts/pptx_server.py`」。
2. 探测成功 -> POST `serializeSvg()` 到 `/export`,收 blob,触发下载 `diagram.pptx`。
3. 成功回显「✓ 完成」,失败回显「✗ 失败」,与现有按钮一致。

HTML 仍自包含可离线;预览 / SVG / Mermaid 不受影响,仅 PPTX 导出依赖本地服务。

## SVG -> DrawingML 映射(保真保证)

| SVG | PPTX (DrawingML) | 保真 |
|-----|------------------|------|
| `<rect rx>` | `<a:prstGeom prst="roundRect">` + `adj=round(rx/min(w,h)×100000)`(上限 50000) | 圆角原生保留,带可拖拽黄点 |
| `stroke-dasharray="5,3"` | `<a:custDash>`(`d=d_raw/sw×100000`,`sp=sp_raw/sw×100000`);命中预设表则 `<a:prstDash>` | 虚线精确保留 |
| `<marker>` 箭头 | `<a:tailEnd type="triangle">`,切到 `prstGeom prst="line"` + flipH/flipV 对齐端点 | 保留 |
| 直线 / 折线 `<path>` | `<p:sp>` + `<a:custGeom>` moveTo / lnTo | 保留(L 形折线解析 `d`) |
| `<text>` | `<p:sp txBox>`,基线补偿 `box_y=y-fontSize×0.85`,`px->pt ×0.75`,`font-weight≥600->b="1"`,CJK 拆 `latin/ea/cs` | 保留 |
| `#hex` | `<a:srgbClr val="...">` | 保留 |
| `opacity` / `fill-opacity` / `stroke-opacity` | `<a:alpha val="int(opacity×100000)">` | 保留 |
| `rgba()` | **不解析 -> noFill**(已知限制,见下) | 丢色 |
| `<pattern>` 网格 | pattFill(可能为空)/ 预处理剥掉 | 装饰性,可接受丢失 |
| 坐标单位 | 1 SVG px = 9525 EMU;幻灯片尺寸 = viewBox × 9525 | 保留 |

## 配色规则(本期不动)

按用户决策,SKILL.md 配色表保持原样(含 rgba)。**已知限制**:转换器不解析 `rgba()`,使用 rgba 的元素在 PPTX 中失去填充 / 描边。示例 SVG 全程用 hex,不受影响;只有严格按配色表用 rgba 生成的图会丢色。SKILL.md 的 PPTX 小节加一句注明此限制,后续再修。

## 文件改动清单

| 文件 | 改动 |
|------|------|
| `scripts/svg_to_pptx/`(新) | vendoring 8 个核心文件;裁掉对 ppt-master 专属模块的引用(实现时核对 import) |
| `scripts/export_pptx.py`(新) | 薄 CLI + python-pptx 打包胶水;核心函数 `convert_svg_to_pptx` |
| `scripts/pptx_server.py`(新) | stdlib `http.server` 本地服务 |
| `resources/template.html` | 工具栏加第 4 按钮 + `downloadPPTX()` JS |
| `requirements.txt`(新) | `python-pptx>=0.6.21` |
| `SKILL.md` | 新增「PPTX 导出」小节(起服务 + 按钮 / CLI + 映射保证 + rgba 限制说明);工具栏表格改 4 按钮;PowerPoint 兼容性小节改「可编辑形状走 PPTX 导出,SVG 导入仅供网页 / 图片」;验收检查加 PPTX 验收项 |
| `scripts/svg_quality_checker.py` | 增加:HTML 含 `downloadPPTX` 按钮的检查(与现有 toolbar 按钮检查并列) |
| `tests/test_svg_quality_checker.py` | 加 PPTX 按钮检查的测试 |

## 错误处理与风险

- **python-pptx 未装**:`export_pptx.py` / `pptx_server.py` 启动即检测,提示 `pip install -r requirements.txt`。
- **服务未起**:按钮探测失败回显提示,不报错。
- **不支持元素**:转换器对未知视觉标签硬失败(`SvgNativeConversionError`);wrapper 捕获并打印清晰错误。本 skill SVG 词汇表(rect / text / line / path / marker / defs / pattern)均在支持范围内。
- **浏览器 `file://` -> `http://localhost` fetch**:依赖 CORS 头;个别浏览器对 file:// fetch 有 quirks,实现时验证。
- **实现时需验证**:① 转换器是否要求 tspan 预扁平化;② `drawingml_converter` 对 `use_expander` 的引用方式(已 vendoring,安全);③ `width="100%"` / `url(#grid)` 处理(出问题则预处理剥掉网格 rect);④ 文本基线定位偏差(验收时重点看,必要时微调)。

## 测试

- **自动**:`svg_quality_checker.py` 校验 HTML 含 PPTX 按钮;`tests/` 加单测。可选冒烟:对示例 SVG 跑 `export_pptx.py`,校验产物可解压且 slide1.xml 合法。
- **手动验收**(写进 SKILL.md):生成含虚线区域 + 圆角方块 + 箭头的图 -> 起服务 -> 点「导出 PPTX」-> PowerPoint 打开 -> 确认:圆角在、虚线在、箭头在、颜色一致、文字可读、每形状可单独选中编辑。

## 不在范围

- 动画、旁白、笔记、图片媒体、svg-snapshot(图片式)导出 - 均不实现。
- rgba 配色迁移 - 本期不做,记为已知限制。
