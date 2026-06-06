# Architecture Diagram Generator

**用 AI 生成专业架构图，只需要描述你的系统。**

在 [Claude.ai](https://claude.ai) 上安装此 Skill，用自然语言描述你的系统架构，Claude 将自动生成一份自包含的 HTML 文件，内含精美的 SVG 架构图——白色背景、中文界面、简洁专业。

- **无需设计能力** —— 用中文描述你的架构即可
- **快速迭代** —— 让 Claude 增删组件、调整布局、更新样式
- **易于分享** —— 输出为单个 HTML 文件，无需任何特殊软件
- **导出内置** —— Mermaid 源码 / 复制 SVG / 下载 SVG 一键操作

![Version](https://img.shields.io/badge/version-2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude](https://img.shields.io/badge/Claude-Skill-orange)

---

## 🚀 快速开始

### 第一步：安装 Skill

> ⚠️ 适用于 Free、Pro、Max、Team、Enterprise 套餐（需先在 **设置 → 功能** 中启用代码执行）

1. 下载 [`architecture-diagram.zip`](architecture-diagram.zip)
2. 打开 [claude.ai](https://claude.ai) → **自定义** → **技能**
3. 点击 **+** → **+ 创建技能** → **上传技能**，选择 zip 文件
4. 启用该技能

### 第二步：准备架构描述

用 AI 分析你的代码库，或自行编写：

**方式 A：让 AI 分析你的代码库**

在 Claude Code、Cursor、Windsurf 或 ChatGPT 中询问：

```
分析此代码库的架构，列出所有主要组件、
它们之间的连接方式、使用的技术栈以及
任何云服务或集成。格式化为架构图可用的列表。
```

**方式 B：自行编写**

```
- React 前端，调用 Node.js API
- PostgreSQL 数据库
- Redis 缓存
- 部署在 AWS 上，使用 CloudFront CDN
```

**方式 C：从模板开始**

```
一个典型的 SaaS 应用的架构是什么样的？
```

### 第三步：生成架构图

在 [Claude.ai](https://claude.ai)（已安装本 Skill）中发送：

```
使用架构图技能，根据以下描述创建架构图：

[粘贴你的架构描述]
```

然后你可以用对话迭代：*"把 Redis 移到数据库层旁边"*、*"添加 JWT 认证流程"*、*"改用横向布局"*。

---

## 📸 示例

在浏览器中打开以下 HTML 文件查看效果（所有示例内置完整工具栏，可直接复制 Mermaid / SVG）：

| 示例 | 说明 | 文件 |
|------|------|------|
| **Web 应用** | React + Node.js API + PostgreSQL + Redis + JWT | [`examples/web-app.html`](examples/web-app.html) |
| **AWS 无服务器** | CloudFront + API Gateway + Lambda + DynamoDB + S3 + Cognito | [`examples/aws-serverless.html`](examples/aws-serverless.html) |
| **微服务** | Kong API 网关 + 多语言服务（Go/Java/Python）+ Kafka + K8s | [`examples/microservices.html`](examples/microservices.html) |

> 所有示例均为 v2 白色主题，`lang="zh-CN"`，Microsoft YaHei 字体，OKLCH 色彩体系。

---

## 📤 导出

打开生成的 HTML 文件，使用顶部工具栏：

| 按钮 | 功能 |
|------|------|
| **Mermaid** | 复制可编辑的 Mermaid 源码 |
| **复制 SVG** | 复制矢量 SVG 到剪贴板 |
| **下载 SVG** | 下载 `.svg` 矢量文件 |

无需安装任何命令行工具。

---

## ✨ 特性

- **白色简洁主题** —— `oklch(0.955 0.008 250)` 浅色背景，白色卡片容器
- **OKLCH 色彩体系** —— 低饱和度填充 + 强描边，视觉舒适
- **Mermaid 源码可编辑** —— 每个图都附带隐藏的 Mermaid 定义块
- **SVG 矢量输出** —— 高清无限放大，适合文档和幻灯片
- **中文界面** —— Microsoft YaHei 字体，全中文 UI
- **自包含 HTML** —— 所有 CSS 和 JS 内嵌，无需联网加载
- **正交绕行布线** —— 箭头自动避让组件，无交叉
- **质量检查工具** —— Python 脚本验证 SVG 质量

---

## 🎨 配色方案

基于 OKLCH 色彩空间的语义化颜色：

| 组件类型 | 填充色 | 描边色 | 用途 |
|---------|--------|--------|------|
| 前端 / 入口 | `oklch(0.92 0.04 250 / 0.12)` | `oklch(0.55 0.2 250)` | 客户端应用、UI |
| 后端 / 核心 | `oklch(0.92 0.035 170 / 0.12)` | `oklch(0.55 0.17 170)` | 服务、API |
| 数据库 / 存储 | `oklch(0.9 0.05 300 / 0.12)` | `oklch(0.5 0.2 300)` | 数据库、AI/ML |
| 云 / 外部 API | `oklch(0.92 0.04 230 / 0.12)` | `oklch(0.55 0.18 230)` | 云服务、外部 API |
| 安全 | `oklch(0.92 0.06 20 / 0.12)` | `oklch(0.55 0.22 20)` | 认证、加密 |
| 插件 / 消息总线 | `oklch(0.92 0.04 80 / 0.12)` | `oklch(0.55 0.18 80)` | 插件、消息队列 |
| 外部 / 通用 | `oklch(0.92 0.01 260 / 0.12)` | `oklch(0.55 0.03 260)` | 通用组件 |

---

## 📦 安装方式

### Claude.ai（推荐）

1. 下载 [`architecture-diagram.zip`](architecture-diagram.zip)
2. **自定义** → **技能** → **+ 创建技能** → **上传技能**
3. 选择 zip 文件，启用技能

### Claude.ai 项目（替代）

1. 在项目知识中上传 `architecture-diagram.zip`

### Claude Code CLI

```bash
# 全局安装
unzip architecture-diagram.zip -d ~/.claude/skills/

# 或项目本地安装
unzip architecture-diagram.zip -d ./.claude/skills/
```

### 手动安装

确保以下文件可被 Claude 访问：

```
architecture-diagram/
├── SKILL.md                   # 技能指令
├── resources/
│   ├── template.html          # HTML 模板
│   └── routing.js             # SVG 坐标路由参考
├── scripts/
│   └── svg_quality_checker.py # 质量检查工具
└── tests/
    └── test_svg_quality_checker.py  # 单元测试
```

---

## 📐 输出结构

每个生成的 HTML 文件包含：

```
┌─────────────────────────────────────────┐
│  [脉冲点] 项目名称架构图  [Mermaid|复制 SVG|下载 SVG] │  ← 标题栏 + 工具栏
├─────────────────────────────────────────┤
│  [项目简介 · 关键特性 · 技术栈]           │  ← 副标题
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │          SVG 架构图              │   │  ← 矢量图形
│  │  组件框 + 箭头 + 图例 + 层边界   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

简洁设计，**无摘要卡片和页脚**。

---

## 🔧 质量检查

Skill 附带一个 Python 质量检查工具：

```bash
# 检查 HTML 文件
python scripts/svg_quality_checker.py path/to/diagram.html

# 检查 SVG 文件
python scripts/svg_quality_checker.py path/to/diagram.svg

# 发布模式（警告视为错误）
python scripts/svg_quality_checker.py --publish path/to/diagram.html
```

检查项包括：

- **硬错误**：无效 SVG XML、缺少 viewBox、缺少工具栏、缺少 Mermaid 源码脚本、包含 `<script>`/`<foreignObject>`/`<style>` 等禁用元素
- **警告**：缺少 `role="img"`、缺少 `aria-label`、文本溢出风险、箭头与组件重叠、布局间距过小、Mermaid 标签与 SVG 不一致

---

## 💡 提示示例

**Web 应用：**

```
创建一个 Web 应用的架构图：
- React 前端
- Node.js/Express API
- PostgreSQL 数据库
- Redis 缓存
- JWT 认证
```

**AWS 无服务器：**

```
创建一个 AWS 无服务器架构图：
- CloudFront CDN
- API Gateway
- Lambda 函数（Node.js）
- DynamoDB
- S3 静态资源
- Cognito 认证
```

**微服务：**

```
创建一个微服务架构图：
- React Web 和移动客户端
- Kong API 网关
- 用户服务（Go）、订单服务（Java）、商品服务（Python）
- PostgreSQL、MongoDB、Elasticsearch
- Kafka 事件流
- Kubernetes 编排
```

---

## 🛠 技术细节

| 项目 | 说明 |
|------|------|
| 输出格式 | 自包含 HTML（内联 CSS + SVG） |
| SVG viewBox | 默认 1000px 宽，自适应缩放 |
| 字体 | Microsoft YaHei、PingFang SC |
| 背景色 | `oklch(0.955 0.008 250)` 浅灰 |
| 卡片背景 | `oklch(1 0.005 250)` 纯白 |
| 色彩空间 | OKLCH |
| 组件圆角 | `rx="6"`–`"7"` |
| 层级间距 | 最小 30px（水平）、40px（垂直） |
| 绕行规则 | L 形/U 形正交路径，避免对角线 |
| 导出方式 | Mermaid 源码、Clipboard API、Blob 下载 |

---

## 📄 姊妹技能

[process-flow-diagram-generator](https://github.com/Cocoon-AI/process-flow-diagram-generator) —— 用于审批流程、运行手册、自动化流水线等时序性工作流，相同设计语言，不同图形语义。

---

## 📝 许可证

MIT License —— 可自由使用、修改和分发。

## 👥 贡献

欢迎提交 Issue 或 PR：

- 报告 Bug 或功能请求
- 提交代码改进
- 分享你生成的架构图

## 📬 联系方式

**Cocoon AI**
📧 hello@cocoon-ai.com

---

Made with ❤️ by [Cocoon AI](https://cocoon-ai.com)
