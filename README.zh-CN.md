<div align="center">

# claim-to-frame

**把原始材料做成图表、交互页面或短片，并让每个结论都有出处的 Agent Skill。**

[English](README.md) · [简体中文](README.zh-CN.md)

[![Validate](https://img.shields.io/github/actions/workflow/status/Temp0jd/claim-to-frame/validate.yml?branch=main&style=flat-square&label=validate)](https://github.com/Temp0jd/claim-to-frame/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-2F6B5E?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-A64B2E?style=flat-square)](CHANGELOG.md)
[![Agent Skill](https://img.shields.io/badge/agent-skill-8A2BE2?style=flat-square)](SKILL.md)

</div>

---

## 为什么写这个工具

让编程助手解释复杂系统或论文时，我总遇到同一个问题：文字很多，证据和结构很少。读起来很顺，但很难判断它是真的准确，还是只是显得自信。我写了这个 skill，让每个事实主张都有来源锚点，也让解释改用概念真正需要的媒介，而不是默认写一大段文字。

## 这是什么

claim-to-frame 是一个面向 Claude Code、Cursor、Codex 等智能体运行时的 Agent Skill。它不凭记忆写摘要，而是带 agent 走一遍分阶段流程，产出经过检查的解释：结构化回答、图表、离线 HTML 页面，或带时间轴的 Manim/HyperFrames 视频。

仓库根目录包含 `SKILL.md`，智能体运行时可以直接加载。主要交接文件都有契约（`project.json`、`storyboard.json`、`render_manifest.json`、`qa_report.json`）；JSON 文件和媒体由小型 Python 脚本校验。

## 安装方式

全局安装到智能体的技能目录：

```bash
npx skills add Temp0jd/claim-to-frame -g -y
```

或手动克隆至本地技能目录：

```bash
git clone https://github.com/Temp0jd/claim-to-frame.git
mkdir -p ~/.claude/skills
cp -r claim-to-frame ~/.claude/skills/claim-to-frame
```

**环境要求：** 契约校验与脚本运行需要 Python 3.10+；视频 QA 检查需要 FFmpeg/FFprobe；使用 HyperFrames 渲染需要 Node 22+ 与 Chrome / Chromium。

## 快速开始

制作一支解释视频的标准操作流：

```bash
# 1. 初始化项目工作区
python3 scripts/scaffold.py \
  --mode forward --artifact video --renderer hyperframes \
  --title "为什么缓存有用" --language zh-CN --out ./explainers/caches

# 2. 在 project.json 中记录 provider 与模型，并编写 sources.md 和 storyboard.json

# 3. 校验契约文件并执行模型预检
python3 scripts/validate_project.py ./explainers/caches/project.json
python3 scripts/validate_storyboard.py ./explainers/caches/storyboard.json
python3 scripts/preflight_model.py ./explainers/caches/project.json --registry assets/model-registry.example.json

# 4. 渲染单镜头试片（试片无音轨；最终混音后再传 --require-audio）
scripts/render_hyperframes.sh ./explainers/caches/render/hyperframes ./explainers/caches/render/out.mp4
python3 scripts/qa_video.py ./explainers/caches/render/out.mp4 --project caches \
  --storyboard ./explainers/caches/storyboard.json
```

## 工作原理

流程有 9 个阶段。每个阶段都有门禁，JSON 契约由脚本校验；门禁未通过就停下来，避免继续消耗时间和 token。

```mermaid
flowchart LR
  A[0 接单<br/>模型计划] --> B[1 来源<br/>主张台账]
  B --> C[2 策略<br/>视觉隐喻]
  C --> D[3 文案<br/>storyboard.json]
  D --> E[4 视觉系统<br/>style tokens]
  E --> F[5 渲染器<br/>脚手架]
  F --> G[6 试片<br/>一镜 / 30 秒]
  G --> H[7 全片构建]
  H --> I[8 QA<br/>交付]
```

各阶段门禁的准入与准出条件见 [`docs/pipeline.md`](docs/pipeline.md)。

## 模式与产物

本技能支持三种工作模式：
- `forward`（正向）：从零解释一个概念、论文、架构或政策。
- `reverse`（逆向）：将已有视频拆解为带证据锚点的镜头表和分镜数据，用于审查或重新制作。
- `hybrid`（混合）：借用参考样片的叙事节奏与视觉结构，填充新的主张与素材。

### 产物阶梯

根据读者理解所需，选择阶梯上足够解决问题的最低一级：

| 产物 | 阶梯层级 | 适用场景 |
| --- | --- | --- |
| `answer` | 0 | 小而熟的事实型问题 |
| `ste` | 1 | 规范流程、合规说明、术语表与操作审计 |
| `diagram` | 2 | 静态系统架构、层级关系、流程序列与状态机 |
| `html` | 3 | 包含可变参数、滑块交互或多状态分支的机理展示 |
| `video` | 4 | 数学公式推导、动态演变系统与时序直觉 |
| `knowledge-film` | 4 | 2–5 分钟视觉先行短片（16:9 画幅、字幕驱动、紧凑节奏） |

脚手架会先创建这些文件：

```text
explainers/caches/
├── README.md
├── project.json
├── sources.md
├── storyboard.md
├── storyboard.json
├── qa/
└── render/
    └── hyperframes/
        ├── index.html
        └── compositions/scene.html
```

`render_manifest.json` 和 `qa_report.json` 在渲染和 QA 之后生成。

## 模型角色与可替换性

流程设计将管线逻辑与具体模型解耦。项目开始时，Agent 会提示用户为四个角色分别指定 provider 和模型：

- `analysis`（分析）：从原始文档或视频中提取主张、公式和语音转录。
- `storyboard`（分镜）：设计叙事弧线、视觉隐喻与画面动作拆解。
- `implementation`（实现）：编写渲染器代码（GSAP、Manim、Canvas）并执行构建。
- `review`（审核）：审查事实忠实度、视觉清晰度、对比度与时间节奏。

模型选型显式保存在 `project.json` 中：

```json
{
  "models": {
    "analysis":       { "status": "selected", "provider": "command-code", "model": "deepseek/deepseek-v4.1-flash", "selected_by": "user" },
    "storyboard":     { "status": "selected", "provider": "command-code", "model": "deepseek/deepseek-v4.1-flash", "selected_by": "user" },
    "implementation": { "status": "selected", "provider": "command-code", "model": "deepseek/deepseek-v4.1-flash", "selected_by": "user" },
    "review":         { "status": "selected", "provider": "command-code", "model": "deepseek/deepseek-v4.1-flash", "selected_by": "user" }
  }
}
```

系统不会根据 provider 名称自动推断模型，二者均独立显式记录。中途更换模型必须追加到 `model_history`，禁止静默切换。渲染前通过 `scripts/preflight_model.py` 检查模型是否具备所需能力。详见 [`docs/model-selection.md`](docs/model-selection.md)。

## 渲染器支持

渲染器是可替换的后端，共用 `storyboard.json` 中的 `style_tokens`：

| 渲染器 | 适用场景 |
| --- | --- |
| `hyperframes` | HTML/CSS/GSAP、文字排版、UI 控件、代码块与 2D 布局 |
| `manim` | 数学公式推导、坐标系、几何变换与 3D 场景 |
| `remotion` | 基于 React 生态的动画与视频工程 |
| `canvas` | 自定义逐帧 2D 动画渲染 |
| `static` | 独立 SVG/PNG 图表、技术架构图与流程图 |

同一个项目里可以混用渲染器：例如用 Manim 渲染公式推导核心，用 HyperFrames 渲染片头与总结卡片。详见 [`references/renderers.md`](references/renderers.md)。

## 完整示例：Transformer 原理讲解

仓库附带一支 107.9 秒的 Transformer 与自注意力中文讲解视频，用 HyperFrames 渲染，1920×1080、30 fps，带中文旁白和软字幕。

<p align="center">
  <a href="examples/transformer/">
    <img src="examples/transformer/preview.gif" alt="Transformer 讲解视频预览" width="720">
  </a>
</p>

<p align="center">
  <a href="examples/transformer/"><strong>浏览 Transformer 示例工程文件 →</strong></a>
</p>

该示例展示了：
- `sources.md` 中将文案主张逐条关联至原始论文 Vaswani et al. (2017)。
- `storyboard.json` 中单调递增的镜头时间分配与画面动词定义。
- `compositions/scene.html` 中的 HTML/CSS/GSAP 编程式动画实现。
- `qa_report.json` 中的对比度（109 处文字全过 WCAG AA）、布局、运行时、解码和字幕检查结果。

## 质量检查与自动化脚本

仓库提供确定性脚本校验契约文件与媒体产物：

- `scripts/validate_project.py`：校验 `project.json` 是否符合 JSON Schema 并检查阶段状态。
- `scripts/validate_storyboard.py`：检查 `storyboard.json` 的镜头时间单调性及必要动作字段。
- `scripts/preflight_model.py`：预检 `project.json` 中声明的 provider、模型与能力（vision、shell、code）。
- `scripts/qa_video.py`：检查 MP4 的编解码器、黑帧、响度、时长和字幕时间。
- `scripts/retime_storyboard.py`：根据 TTS 旁白实测时长，自动校准 `storyboard.json` 中的镜头起始时间与时长。
- `scripts/check_artifact.py`：检测独立 HTML 解释页面的离线可用性与可访问性。
- `scripts/ste_lint.py`：检查 STE-lite 文本的句子长度与禁用词汇。
- `scripts/check_release.py`：扫描未填写的占位符、泄露的密钥、无效 JSON 及缺失文件。

运行本地检查：

```bash
python3 scripts/validate_examples.py
python3 scripts/check_release.py --strict
```

各类媒体的具体验收标准详见 [`docs/quality-gates.md`](docs/quality-gates.md)。

## 不是什么与当前边界

保持务实的预期：

- **早期版本（v0.2.0）**：文件契约与命令行参数已经可用，但后续仍会根据实际使用持续迭代。
- **不是 SaaS 或桌面端软件**：这是一个配合命令行和本地智能体运行时的 Agent Skill。
- **不是自动事实核查器**：流程强制要求主张在 `sources.md` 中提供锚点，但无法保证原始来源本身必然正确。
- **仍需人工审核**：模型可能误判画面留白与时间节奏，试片门禁的核心目的就是让人在渲染全量前直观检查画面。

## 仓库结构

<details>
<summary>点击展开仓库目录结构</summary>

```text
claim-to-frame/
├── SKILL.md                  # 智能体运行时加载的技能指令
├── README.md                 # 英文文档
├── README.zh-CN.md           # 中文文档
├── docs/                     # 流程阶段、模型选型与质量门禁指南
├── references/               # STE、图表、HTML 与各渲染器参考手册
├── assets/                   # 项目模板、style tokens 预设与模型注册表示例
├── schemas/                  # 各交接文件的 JSON Schema 契约
├── scripts/                  # 脚手架、校验器、预检、QA 与发布检查工具
├── tests/                    # 自动化 pytest 测试用例
├── examples/transformer/     # 包含完整视频与契约文件的 HyperFrames 示例
└── .github/workflows/        # CI 自动化工作流
```

</details>

## 致谢

本项目由 Tempo 发起，继承自早期的 `explain-anything` 工作流，并参考了以下开源项目：

- **vibe-knowledge-film** (MIT) — 视觉先行视频结构、镜头表规范与试片评审方法。
- **HyperFrames** (Apache-2.0) — HTML/CSS/GSAP 编排契约与渲染工作流。
- **Manim Community** (MIT) — 编程式数学动画引擎。

授权信息与边界说明详见 [`NOTICE.md`](NOTICE.md)。

## 开源许可

MIT 许可证。详见 [`LICENSE`](LICENSE)。
