# Architecture Diagram Generator

> 让系统说明变成一张能讲清边界、结构和数据流的专业架构图。
> 适合 README 首页、方案汇报、培训材料和产品演示。

![Version](https://img.shields.io/badge/version-2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

![architecture diagram overview](examples/architecture-diagram-overview.svg)

## 一眼看懂

| 你提供 | 它生成 | 结果价值 |
|------|------|------|
| 一段自然语言 | 单文件 HTML | 打开即看，离线可用 |
| 结构描述 | Mermaid 源码 | 后续修改更方便 |
| 图形需求 | SVG 矢量图 | 可直接用于文档和 PPT |
| 中文系统说明 | 白底中文架构图 | 更适合团队沟通和汇报 |

## 产品亮点

| 亮点 | 说明 |
|------|------|
| 自然语言输入 | 不需要先会画图，只要把系统讲清楚 |
| 单文件交付 | 所有样式和脚本内嵌，方便分享与归档 |
| 双重输出 | 同时保留 Mermaid 源码和 SVG 成品 |
| PowerPoint 兼容 | 导出的 SVG 可直接拖入 PPT，颜色保持正常 |
| 内置质量检查 | 导出前可以先校验 HTML 和 SVG |
| 中文界面 | 适合中文团队、文档和培训场景 |

## 和传统绘图平台的不同

`draw.io`、`Excalidraw` 也能用文字辅助生成流程图，但 `Architecture Diagram Generator` 的重点不在“通用画图”，而在“从现有资产直接生成架构图”。它更适合把设计文档、代码目录和系统说明，快速整理成能交付、能复用、能继续编辑的架构表达。

- 基于设计文档生成
  可以从 PRD、技术方案、架构说明中提取系统边界、组件关系和关键链路。
- 基于代码目录生成
  可以从项目目录结构、模块命名和代码组织方式，推导出分层结构与核心组件。
- 面向架构图，而不是通用画布
  输出更强调系统边界、依赖关系、数据流和技术分层，而不是自由摆放图形。
- 输出可继续编辑，不只是静态图片
  生成结果同时保留 Mermaid 源码和 SVG 矢量图，既能直接展示，也能继续修改和迭代。
- 适合把已有项目快速可视化
  当你已经有设计文档或代码仓库时，可以直接把它们变成可读的架构图，而不必从空白画布重画一遍。

## 安装方式

这个项目按业内常见的 `skills` 目录方式分发：把整个 `architecture-diagram/` 目录放进 AI 助手识别的技能目录，并确保 `SKILL.md` 位于根目录。安装完成后刷新技能列表，或重启客户端即可生效。

### Codex

```bash
cp -r architecture-diagram ~/.codex/skills/
```

如果你使用 Codex 的技能安装器，也可以从仓库路径直接安装，安装完成后重启 Codex。

### Claude Code

```bash
cp -r architecture-diagram ~/.claude/skills/
```

安装后执行 `/skills reload`，或者直接重启 Claude Code。

### opencode

```bash
cp -r architecture-diagram ~/.opencode/skills/
```

也可以把 `architecture-diagram/` 放在项目本地，由 opencode 自动发现。

### 其他 AI 助手

把 `architecture-diagram/` 放入对应助手识别的 `skills` 目录即可。常见路径包括 `.github/skills/`、`.claude/skills/`、`.agents/skills/` 等。

### 安装原则

- 复制整个目录，不要只拷贝 `SKILL.md`
- 保持目录结构不变
- 安装后刷新或重载技能缓存


## 使用说明

你只需要把“要画什么”说明清楚，剩下的排版、连线和视觉组织可以交给它。

## 具体使用示例

### 示例一：基于设计文档生成架构图

适合你已经有 PRD、技术方案或架构说明，只想把文字内容快速整理成一张对外可展示的图。

```text
请基于XXX文档生成架构图
```

预期效果：

- 一张清晰的系统架构图
- 重点链路被高亮展示
- 组件关系、数据流向和依赖关系一目了然

### 示例二：基于代码目录生成架构图

适合你已经有一个代码仓库，希望根据目录结构和模块职责快速生成架构图。

```text
请根据XXX目录下的代码生成架构图。

```

预期效果：

- 按目录和职责自动整理出分层架构
- 业务模块与基础设施边界更清楚
- 适合技术文档、代码评审和知识库沉淀

### 生成后你会得到

| 输出 | 作用 |
|------|------|
| HTML | 直接打开预览，适合分享和演示 |
| Mermaid | 便于继续编辑和版本迭代 |
| SVG | 适合文档、PPT 和知识库嵌入 |

### 想让图更好看，可以这样描述

- 先说系统边界，再说核心组件
- 组件数量尽量控制在 3 到 7 个
- 如果有重点，明确告诉它是“突出调用链路”还是“突出分层结构”
- 如果有多条链路，说明哪条是主链路、哪条是辅助链路


## 输出与工具栏

每个生成的 HTML 都包含三个按钮：

| 按钮 | 功能 |
|------|------|
| Mermaid | 复制可编辑的 Mermaid 源码 |
| 复制 SVG | 复制矢量 SVG 到剪贴板 |
| 下载 SVG | 导出 `.svg` 文件 |

> 建议优先保留 Mermaid 源码，便于后续改图与版本迭代。

## 视觉语言

这个项目默认采用“白底 + 轻阴影 + 语义化配色”的视觉路线，目标是让图看起来干净、专业、适合报告和文档。

| 设计项 | 取向 |
|------|------|
| 背景 | 白底为主 |
| 卡片 | 轻阴影、圆角矩形 |
| 连线 | 优先正交折线，减少交叉 |
| 配色 | 低饱和、语义化、同类同色系 |
| 字体 | 中文优先，适合屏幕与演示 |

## 项目结构

```text
architecture-diagram/
├─ README.md
├─ LICENSE
├─ examples/
│  └─ architecture-diagram-overview.svg
└─ architecture-diagram/
   ├─ SKILL.md
   ├─ resources/
   │  ├─ template.html
   │  └─ routing.js
   ├─ scripts/
   │  └─ svg_quality_checker.py
   └─ tests/
      └─ test_svg_quality_checker.py
```

## 许可证

MIT License，允许自由使用、修改和分发。

## 贡献

欢迎提交 Issue 或 PR。
