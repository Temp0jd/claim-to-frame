<div align="center">

# claim-to-frame

**把原始材料做成图表、交互页面或知识短片，并让每个结论都有出处。**

[English](README.md) · [简体中文](README.zh-CN.md)

[![Validate](https://img.shields.io/github/actions/workflow/status/Temp0jd/claim-to-frame/validate.yml?branch=main&style=flat-square&label=validate)](https://github.com/Temp0jd/claim-to-frame/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-2F6B5E?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-A64B2E?style=flat-square)](CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](requirements.txt)
[![Agent Skill](https://img.shields.io/badge/agent-skill-8A2BE2?style=flat-square)](SKILL.md)
[![Model-agnostic](https://img.shields.io/badge/models-swappable-4F6F5D?style=flat-square)](docs/model-selection.md)

</div>

---

技术解释常常默认写成段落，即使这个概念更适合图表、交互页面或动态画面。

**claim-to-frame** 是一个 Agent Skill，把原始文献、设计文档或已有视频做成解释产物。它先把主张整理成台账（claim ledger），再选择介质，最后交付经过检查的成品：例如可离线打开的交互页面，或带旁白和字幕的知识短片。

## 快速开始

安装到智能体的技能目录：

```bash
npx skills add Temp0jd/claim-to-frame -g -y
```

或手动安装：

```bash
git clone https://github.com/Temp0jd/claim-to-frame.git
mkdir -p ~/.claude/skills
cp -r claim-to-frame ~/.claude/skills/claim-to-frame
```

Python 3.10+ 可运行契约和脚本；视频 QA 需要 FFmpeg/FFprobe；HyperFrames 需要 Node 22+ 和 Chrome。各渲染器的依赖见 [`references/renderers.md`](references/renderers.md)。

初始化项目与执行校验流程：

```bash
# 1. 创建项目工作区
python scripts/scaffold.py \
  --mode forward --artifact video --renderer hyperframes \
  --title "为什么缓存有用" --language zh-CN --out ./explainers/caches

# 2. 在 project.json 中记录所选的 provider 与模型，并编写 sources.md 和 storyboard.json

# 3. 校验契约文件并执行模型预检
python scripts/validate_project.py ./explainers/caches/project.json
python scripts/validate_storyboard.py ./explainers/caches/storyboard.json
python scripts/preflight_model.py ./explainers/caches/project.json --registry assets/model-registry.example.json

# 4. 在全片构建前先渲染一镜试片
scripts/render_hyperframes.sh ./explainers/caches/render/hyperframes ./explainers/caches/render/out.mp4
python scripts/qa_video.py ./explainers/caches/render/out.mp4 --project caches \
  --storyboard ./explainers/caches/storyboard.json
# 试片没有音轨；混入旁白后再加 --require-audio。
```

## 是什么与不是什么

| 是什么 | 不是什么 |
| --- | --- |
| 一个 Agent Skill，加一套分阶段流程 | npm 代码库、独立 CLI 或桌面应用 |
| 有 JSON Schema 契约和阶段门禁的流程 | 一堆提示词或直接套用的模板 |
| 模型无关：分析、分镜、实现、审核四个角色显式选择 | 绑定某一个模型的封装 |
| 来源可追溯：每个事实主张都有锚点 | 没有来源、直接生成结论的工具 |
| 渲染器无关：Manim、HyperFrames、Remotion、Canvas 或静态 HTML | 只服务 Manim 的导出脚本 |

## 工作原理

流程把解释产物的生产拆成若干阶段。主要交接文件都有明确契约，JSON 文件会按 schema 校验。某个阶段的门禁未通过时，流程会停下来，直到产物修复。

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

各阶段的进入和通过条件见 [`docs/pipeline.md`](docs/pipeline.md)。

## 模式与产物

### 三种工作模式

- `forward`（正向）：从零解释一个概念、论文、系统或政策。
- `reverse`（逆向）：把已有视频拆成带证据锚点的镜头表和分镜，用来审查或重做。
- `hybrid`（混合）：借用参考视频的节奏和视觉结构，换成新的主张和素材。

### 产物阶梯

按读者要解决的问题，选最轻的产物：

| 产物 | 阶梯层级 | 适用场景 |
| --- | --- | --- |
| `answer` | 0 | 小、熟、事实型问题 |
| `ste` | 1 | 术语、流程、合规和审计 |
| `diagram` | 2 | 结构、层级、流程和状态 |
| `html` | 3 | 有参数、分支或多层结构的机制 |
| `video` | 4 | 随时间变化的推导、系统行为或直觉 |
| `knowledge-film` | 4 | 2–5 分钟、16:9、无旁白、底部字幕、视觉先行 |

## 模型无关的角色选择

流程和模型分开。项目开始时，Agent 会问四个角色分别用哪个 provider 和模型：

- `analysis`（分析）：读参考资料、转录、数据表和关键帧。
- `storyboard`（分镜）：写叙事、设计视觉、拆分镜和画面动作。
- `implementation`（实现）：写渲染器代码并跑构建。
- `review`（审核）：检查事实、可读性、字幕同步和对比度。

选择写进 `project.json`：

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

provider 和模型分开记录，不根据 provider 名称猜模型；更换 provider 或模型必须写入 `model_history`，不能静默替换。在渲染开始前，`scripts/preflight_model.py` 会校验所选模型是否满足必要的能力要求。详见 [`docs/model-selection.md`](docs/model-selection.md)。

## 渲染器支持

渲染器是可替换的后端：

| 渲染器 | 适用场景 |
| --- | --- |
| `hyperframes` | HTML/CSS/GSAP、排版、UI、图表、代码 |
| `manim` | 公式、坐标轴、几何、LaTeX、3D 数学 |
| `remotion` | 已有 React/Remotion 工程 |
| `canvas` | 自定义逐帧 2D 动画 |
| `static` | SVG/PNG 图表、海报和流程图 |

也可以混用：Manim 做数学主体，HyperFrames 做片头、章节卡和片尾，共用 style tokens。详见 [`references/renderers.md`](references/renderers.md)。

## 完整示例：Transformer 原理讲解

仓库附带一支 107.9 秒的 Transformer 中文讲解视频，用 HyperFrames 渲染，浅色学术风。

<p align="center">
  <a href="examples/transformer/">
    <img src="examples/transformer/preview.gif" alt="Transformer 讲解视频预览" width="720">
  </a>
</p>

<p align="center">
  <a href="examples/transformer/"><strong>浏览 Transformer 示例工程文件 →</strong></a>
</p>

示例展示了：
- `sources.md` 把文案里的核心主张追溯到 Vaswani et al. (2017)。
- `storyboard.json` 记录单调的镜头时间、画面动作和验收条件。
- `compositions/scene.html` 是 HTML/CSS/GSAP 源码。
- 在 `qa_report.json` 中记录对比度、布局、运行时、解码和字幕检查结果。

## 质量门禁与校验工具

主要产物会经过确定性脚本和门禁检查：

| 质量门禁 | 检验范围与执行方式 |
| --- | --- |
| 来源台账 | 每个数值、定义、公式和因果论断都有明确来源锚点。 |
| 模型预检 | `scripts/preflight_model.py` 检查 provider、模型和所需能力。 |
| 分镜契约 | `scripts/validate_storyboard.py` 检查时间单调、动作和验收条件。 |
| 音频对齐 | `scripts/retime_storyboard.py` 用实测 TTS 时长重写分镜时间。 |
| 视频质检 | `scripts/qa_video.py` 检查流、响度、黑帧、解码和字幕。 |
| 发布扫描 | `scripts/check_release.py` 检查占位符、本机绝对路径、凭证泄漏、无效 JSON 和缺失文件。 |

本地验证：

```bash
python -m pytest
python scripts/validate_examples.py
python scripts/check_release.py --strict
```

## 仓库结构

<details>
<summary>展开目录结构</summary>

```text
claim-to-frame/
├── SKILL.md                  # Agent Skill 入口
├── README.md                 # 英文文档
├── README.zh-CN.md           # 中文文档
├── docs/                     # 流程、模型选择、契约和 QA
├── references/               # STE、图表、HTML、视频和渲染器参考
├── assets/                   # 模板、style tokens 和模型注册表
├── schemas/                  # 各交接文件的 JSON Schema
├── scripts/                  # 脚手架、校验、预检、QA、重定时、发布检查
├── tests/                    # pytest 测试
├── examples/transformer/     # 包含完整视频与契约文件的 HyperFrames 示例
└── .github/workflows/        # CI
```

</details>

## 设计原则

1. **形式服从理解**：若一张带有清晰标注的架构图已能讲明机理，就不要过度制作成视频。
2. **先立锚点，后拟文案**：每个核心事实必须先关联确凿来源，再组织脚本语句。
3. **先定画面，后写解说**：制作视频时，在撰写旁白前必须先明确具体的物理或空间视觉主体。
4. **动词必须在画面中发生**：当解说提到“过滤”时，画面必须同步呈现元素被剔除的动作。
5. **统一的视觉世界**：全片保持统一的色彩搭配、空间比例与视觉隐喻，避免杂乱拼接。
6. **先做试片，再铺全量**：在大规模构建之前，先渲染 30 秒试片验证布局美感与时间节奏。
7. **模型可换，契约不换**：所有模型选型必须记录在 `project.json` 中，禁止无记录的隐式替换。
8. **求真重于形式**：一段朴素无华但逻辑准确的文字，远胜过一段视觉华丽却误导机理的动画。

## 致谢

本项目基于作者此前的 `explain-anything` 项目，并参考了：

- **vibe-knowledge-film** (MIT) — 视觉先行知识短片流程、镜头表和逐帧检查。https://github.com/HeyChengC/vibe-knowledge-film
- **HyperFrames** (Apache-2.0) — HTML/CSS/GSAP 组合契约和 CLI。https://github.com/heygen-com/hyperframes
- **Manim Community** (MIT) — 数学动画引擎。https://www.manim.community/

许可与边界见 [`NOTICE.md`](NOTICE.md)。

## 许可

MIT。见 [`LICENSE`](LICENSE)。
