---
name: architecture-diagram
description: Use when creating architecture overview diagrams or flowcharts that need Mermaid source, HTML preview, and premium SVG output with Chinese UI and a white background.
---

# Architecture Diagram Generator

创建专业的架构概览图和流程图，输出自包含的 HTML 文件，含内联 SVG 矢量图形、中文界面、白色背景，支持 Mermaid 源码编辑和 SVG 导出。

> **Version 2.0** · MIT License · 源于 Cocoon AI

## 快速上手

```
architecture-diagram/
├── SKILL.md                      # 本说明文档
├── resources/
│   ├── template.html             # 输出模板（核心文件）
│   └── routing.js                # 箭头绕行参考
├── scripts/
│   └── svg_quality_checker.py    # 质量检查工具
└── tests/
    └── test_svg_quality_checker.py
```

### 部署到 AI 编程助手

**opencode** — 将 `architecture-diagram/` 复制到 `~/.opencode/skills/` 目录：

```bash
cp -r architecture-diagram ~/.opencode/skills/
```

**其他助手** — 将仓库代码放入对应系统的 skill 目录即可。AI 助手读取 `SKILL.md` 后即可按规范生成架构图。

### 手动使用

不依赖 AI 助手也能用：打开 `resources/template.html`，按注释修改 SVG 坐标和文字，在浏览器中预览效果。质量检查器独立运行：

```bash
python scripts/svg_quality_checker.py path/to/diagram.html
```

## 适用场景

### 架构概览图

展示系统边界、主要组件、分层结构和数据流。适用于：

- 项目 README 中的系统架构说明
- 技术方案评审文档
- 团队内部知识沉淀

### 流程图

展示步骤流程、决策分支、状态流转。适用于：

- **SPEC / SRS 文档转流程图** — 将产品需求规格中的业务逻辑提取为可视化流程图，帮助开发和测试快速理解
- 接口调用时序
- CI/CD 流水线
- 算法流程说明

### 典型业务流程

从需求文档到流程图：

```
[SPEC 文档] → [提取关键流程节点] → [编排 Mermaid 定义] → [生成 SVG HTML]
```

AI 助手读取 SPEC 文档后，识别其中的业务流转逻辑，自动生成对应的流程图 HTML，包含层边界、节点、连线、分支条件。

## 设计规范

### 制图质量要求

- 逻辑自洽：每个组件、箭头、标签都应反映真实的系统边界或数据流
- 配色克制：优先低饱和度填充 + 较高饱和度描边，避免霓虹色、纯黑边框、过亮红色
- 连线不穿框：箭头/连线不得穿过组件方块。无法避免时先调整布局，而非强行交叉
- 正交优先：默认 L 形折线绕行，仅在路径完全通畅时才使用直线
- 箭头标签精简：避开角落、边界和其他标签
- 成品应一目了然，不拥挤

### 色板

> **重要：PowerPoint 兼容性**
> SVG 中必须使用十六进制或 `rgba()` 颜色，**不得使用 `oklch()`**。PowerPoint 导入 SVG 时不支持 OKLCH 色彩空间，会导致所有形状变黑。OKLCH 仅在 HTML 页面 CSS 中用于浏览器渲染，SVG 元素一律用 hex 或 rgba。

组件语义色（白色背景上，SVG 中使用左侧十六进制值）：

| 组件类型 | 填充（SVG 用） | 描边（SVG 用） |
|---------|---------------|----------------|
| 前端 / 入口 | `#eaf0fa` | `#5a82c2` |
| 后端 / 核心 | `#e2f1ed` | `#4a9e91` |
| 数据库 / 存储 | `#ede6f5` | `#7a62a8` |
| 云服务 / 外部 API | `#e6edf7` | `#5a87c2` |
| 安全 / 认证 | `#fce8e0` | `#d47a5a` |
| 插件 / 消息总线 | `#e8f2e2` | `#72a44e` |
| 外部 / 通用 | `#efeff1` | `#86868c` |

虚线区域边框（SVG 中用 `rgba`）：

| 区域类型 | 边框（SVG 用） | 底色（SVG 用） |
|---------|---------------|----------------|
| 前端区域 | `rgba(90,130,194,0.34)` | `#f2f6fb` |
| 后端区域 | `rgba(74,158,145,0.34)` | `#eef8f5` |
| 数据库区域 | `rgba(122,98,168,0.34)` | `#f5f0fa` |
| 通用区域 | `rgba(134,134,140,0.3)` | `#f4f4f5` |

中性色（SVG 中用左侧十六进制值）：

| 元素 | SVG 颜色 | CSS 颜色（浏览器） |
|------|----------|-------------------|
| 页面背景 | `#ffffff` | `#ffffff` |
| 卡片背景 | `#ffffff` | `#ffffff` |
| 正文 | `#2d2d33` | `#2d2d33` |
| 辅助文字 | `#808088` | `#808088` |
| 边界 / 分割线 | `#d8d8dc` | `#d8d8dc` |
| 箭头 / 网格线 | `#929298` / `#e8e8ed` | `#929298` / `#e8e8ed` |
| 白色文字 | `#ffffff` | `#ffffff` |

### 排版

```css
font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif;
```

层级通过字重 + 字号对比实现（相邻级别字号比 ≥1.25）：

| 元素 | 字号 | 字重 |
|------|------|------|
| 标题 | 18px | 650 |
| 副标题 | 13px | 420 |
| 组件名 | 12–13px | 620–650 |
| 说明文字 | 9–10px | 400 |
| 箭头标签 | 9px | 500 |
| 层标签 | 10px | 600 |

### 视觉元素

**背景:** 白色页面 + 白色卡片容器，卡片带轻微阴影：
```css
body { background: #ffffff; }
.container { background: #ffffff; box-shadow: 0 1px 2px oklch(0 0 0 / 0.04), 0 8px 24px oklch(0 0 0 / 0.06); }
```

**脉冲点:** 标题栏动态指示器：
```css
.pulse-dot { width: 10px; height: 10px; border-radius: 50%; background: #5a82c2; animation: pulse 2.4s ease-in-out infinite; }
```

**网格背景:** SVG 画布底部极浅网格线：
```svg
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
  <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#e8e8ed" stroke-width="0.5"/>
</pattern>
```

**层标签:** 填充圆角矩形 + 白色文字（填充色用对应组件描边色的十六进制值）：
```svg
<rect x="X" y="Y" width="84" height="20" rx="4" fill="COMPONENT_STROKE_HEX" />
<text x="CX" y="Y+14" fill="#ffffff" font-size="10" font-weight="600" text-anchor="middle">层名称</text>
```

**组件方块:** 圆角矩形（`rx="6"–7`），1.3–1.5px 描边，半透明填充。

**区域边界:** 虚线描边（`stroke-dasharray="5,3"`），匹配组件色，微透明底色。

**箭头:** SVG marker 箭头头，画在组件方块之前（位于底层）。

**箭头标签:** 白色圆角药丸形背景，避免被网格线干扰。

### 布局规则

- **组件高度:** 服务 55px，大分组 60-85px
- **同级水平间距:** ≥30px
- **上下层垂直间距:** ≥40px
- **层边界内边距:** 距最外侧组件 15-20px
- **图例偏移:** 距最低元素 ≥15px
- **箭头端点偏移:** 距目标边缘 2px
- **箭头标签位置:** 居中于连接边之间，距箭头线 ±8px

### 布局结构

1. **表头** — 标题 + 脉冲指示点 + 导出工具栏
2. **SVG 主图** — 放在圆角边框卡片内
3. **无底部卡片或页脚** — 保持输出简洁

## 导出工具栏

每个 HTML 自带三个按钮：

| 按钮 | 功能 |
|------|------|
| Mermaid | 复制 Mermaid 源码到剪贴板 |
| 复制 SVG | 复制 SVG XML 到剪贴板 |
| 下载 SVG | 下载 .svg 文件 |

模板中必须保留的元素：
- `id="report-container"` 在 `.container` 上
- `.toolbar` + `.toolbar-btn` 按钮
- `@media print { .toolbar { display: none !important; } }`
- `copyMermaid()`, `copySVG()`, `downloadSVG()` 函数
- 模板不得引入外部图片导出库

## 组件方块模板

> SVG 中必须使用十六进制颜色，不得使用 `oklch()`，否则 PowerPoint 导入后颜色变黑。

```svg
<rect x="X" y="Y" width="W" height="H" rx="7" fill="FILL_HEX" stroke="STROKE_HEX" stroke-width="1.3"/>
<text x="CX" y="Y+22" fill="#2d2d33" font-size="12" font-weight="620" text-anchor="middle">NAME</text>
<text x="CX" y="Y+38" fill="#808088" font-size="9" text-anchor="middle">说明文字</text>
```

## 箭头绕行参考

详见 `resources/routing.js`：

- **L 形:** 先垂直再水平（不同行/列的组件）
- **U 形:** 绕障碍物走宽再折回
- **绕障碍:** 穿过相邻组件间的窄缝

### 边界检测清单

放置完所有组件并画箭头前，逐项确认：

```
[ ] 无组件矩形重叠
[ ] 箭头端点距目标边缘 2px
[ ] 箭头中间段不穿过任何组件矩形
[ ] 箭头标签不重叠任何矩形
[ ] 无箭头交叉（平行线可接受，X 形交叉不可）
[ ] 层边界距最外侧组件 ≥15px
[ ] 图例距最低元素 ≥15px
[ ] viewBox 高度容纳全部内容，底部留 10-20px 空白
```

### 验收检查

**声称完成前，逐条执行：**

1. 在浏览器中打开 `.html` 文件
2. 目视确认：无箭头穿过方块
3. 目视确认：所有标签清晰可读
4. 运行质量检查器检查 HTML 预览和导出的 SVG
5. 测试导出工具栏的三个按钮
6. 下载 SVG → 拖入 PowerPoint → 目视确认颜色正常、无全黑方块
7. 发现问题 → 修复坐标或标记 → 回到步骤 1

## 质量检查器

运行方式：

```bash
python scripts/svg_quality_checker.py path/to/diagram.html
python scripts/svg_quality_checker.py path/to/diagram.svg
python scripts/svg_quality_checker.py --publish path/to/diagram.html
python scripts/svg_quality_checker.py --publish path/to/diagram.svg
```

硬错误（必须通过）：

- 无效 SVG XML
- 缺少 `viewBox`
- HTML 中缺少 `toolbar` / `mermaid-src`
- HTML 中缺少 Mermaid / SVG 导出按钮
- SVG 中包含禁止元素：`script`, `foreignObject`, `style`

警告：

- 缺少 `role="img"`
- 缺少 `aria-label`
- `viewBox` 格式异常
- width/height 与 `viewBox` 不匹配

发布前请用 `--publish` 模式（将警告视为错误）。迭代过程中可用普通模式。

## Mermaid 导出

架构图和流程图都以 Mermaid 作为可编辑源定义。

### SVG ↔ Mermaid 映射

| SVG 元素 | Mermaid | 说明 |
|---------|---------|------|
| 入口组件 | `A([text])` | 跑道圆角 |
| 核心服务 | `A[text]` | 直角矩形 |
| 存储/数据库 | `A[(text)]` | 圆柱形 |
| 外部 API | `A([text])` | 跑道圆角 |
| 层边界 | `subgraph 名称 ... end` | 虚线矩形 |
| 箭头 | `-->` / `--\|标签\|-->` | 连线 |
| 说明行 | `A[名称<br/>说明]` | `<br/>` 换行 |
| 图方向 | `flowchart TD` / `flowchart LR` | 纵向 / 横向 |

### 完整示例

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

- 多层多色可用 `classDef` 为不同子图内节点单独赋色
- 复杂绕行箭头在 Mermaid 中简化为直接连线
- 默认 `flowchart TD` + 子图内 `direction LR`（层间纵向、层内横向）

### 自检清单

```
[ ] Mermaid 语法正确
[ ] 与 SVG 内容一致（节点、层级、连接关系）
[ ] 浏览器预览正常，SVG 导出清晰
[ ] `python scripts/svg_quality_checker.py path/to/diagram.html` 无错误
[ ] `python scripts/svg_quality_checker.py path/to/diagram.svg` 无错误
[ ] SVG 中无 oklch()（用 hex 或 rgba 替代）
[ ] PowerPoint 导入后颜色正常
```

## 输出规范

始终输出自包含的单个 `.html` 文件：

- 内联 CSS
- 内联 SVG（无外部图片）
- 纯 SVG 绘图；仅导出工具栏和 Mermaid 复制功能允许少量 JavaScript
- 导出按钮：Mermaid · 复制 SVG · 下载 SVG

### PowerPoint 兼容性

SVG 导出后若需导入 PowerPoint，必须遵守以下规则，否则颜色会渲染为全黑：

1. **SVG 内所有颜色必须使用十六进制（`#xxxxxx`）或 `rgba()`，禁止使用 `oklch()`**
2. CSS 中的 `oklch()` 不受影响（不进入 SVG）
3. `rgba()` 在半透明场景（虚线区域边框、箭头标签背景）下兼容 PPT 2016+
4. 验证方式：下载 SVG → 拖入 PowerPoint → 目视确认各组件颜色与 HTML 预览一致
