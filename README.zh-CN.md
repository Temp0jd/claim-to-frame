# explain-anything

> 把复杂材料变成“为理解而设计”的产物：流程固定，模型可换。

[![Validate](https://github.com/Temp0jd/explain-anything/actions/workflows/validate.yml/badge.svg)](https://github.com/Temp0jd/explain-anything/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/agent-skill-8A2BE2.svg)](SKILL.md)

大多数解释失败，是因为它们优化的是“文字”，不是“理解”。这个 skill 先判断概念需要哪种表达，再证明表达没有歪曲原意。

它**不绑定模型**：流程固定，但分析、分镜、实现、审核四个角色使用什么模型，由用户在开始时明确选择，并记录在 `project.json`。

## 能做什么

- **正向模式**：解释概念、论文、系统、政策或决策。
- **逆向模式**：把已有视频拆成有证据锚点的镜头表和分镜，再重建或改写。
- **产物阶梯**：校准过的回答 → STE-lite 文本 → 图表 → 离线 HTML → Manim/HyperFrames 视频 → 2–5 分钟知识短片。
- **来源可追溯**：每个数字、人名、日期、公式、因果判断都有出处。
- **视觉先行**：先找到观众认得的形象，再写文案；主体要像它本身，句子里的动词要在屏幕上真的发生。

## 为什么模型无关

开始时，Agent 会明确问：

> 分析、分镜、实现、审核四个角色，分别用哪个 provider 和模型？可以说“全部同一个”“自动推荐”，也可以逐个指定。

选择会写进：

```json
{
  "models": {
    "analysis": { "status": "selected", "provider": "...", "model": "...", "selected_by": "user" },
    "storyboard": { "status": "selected", "provider": "...", "model": "...", "selected_by": "user" },
    "implementation": { "status": "selected", "provider": "...", "model": "...", "selected_by": "user" },
    "review": { "status": "selected", "provider": "...", "model": "...", "selected_by": "user" }
  }
}
```

中途换 provider 或模型会写入 `model_history`，并重跑受影响阶段；不允许静默切换。详见 `docs/model-selection.md`。

## 模式与产物

| 模式 | 输入 | 输出 |
| --- | --- | --- |
| `forward` | 概念、论文、系统、政策、笔记 | 解释产物 |
| `reverse` | 已有视频 / 演讲 / 动画 | `analysis.json` + `storyboard.json`，可选重建 |
| `hybrid` | 参考视频 + 新主题 | 复用结构，不复用观点或素材 |

| 产物 | 适合 |
| --- | --- |
| `answer` | 小、熟、事实型问题 |
| `ste` | 术语、流程、合规、审计 |
| `diagram` | 结构、层级、流程、状态 |
| `html` | 有变量、反事实、分层的机制 |
| `video` | 随时间变化、推导、直觉 |
| `knowledge-film` | 2–5 分钟、16:9、无旁白、底部字幕、视觉先行 |

## 流程

```text
0 接单 + 模型计划
1 来源 + 主张清单
2 解释策略 + 视觉隐喻
3 文案 + storyboard.json
4 视觉系统 + style tokens
5 渲染器 + 脚手架
6 试片（一镜 / 30 秒）
7 全片构建
8 QA + 交付
```

每一阶段都有门禁；门禁不过不进入下一阶段。详见 `docs/pipeline.md`。

## 渲染器

| 渲染器 | 适合 |
| --- | --- |
| `manim` | 公式、坐标轴、几何、LaTeX、3D 数学 |
| `hyperframes` | HTML/CSS/GSAP、排版、UI、图表、代码、动态字 |
| `remotion` | 已有 React/Remotion 工程 |
| `canvas` | 自定义逐帧 2D 知识短片 |
| `static` | 图表、海报、单帧解释 |

可以混合：Manim 做数学主体，HyperFrames 做片头/章节卡/片尾，共用 `style_tokens`。详见 `references/renderers.md`。

## 快速开始

```bash
git clone https://github.com/Temp0jd/explain-anything.git
cd explain-anything

python scripts/scaffold.py \
  --mode forward --artifact video --renderer hyperframes \
  --title "为什么缓存有用" --language zh-CN --out ./explainers/caches

# 1. Agent 询问四个角色分别用什么 provider 和模型
# 2. 把选择写进 ./explainers/caches/project.json
# 3. 填写 sources.md 和 storyboard.json
# 4. 复制 assets/model-registry.example.json 为 model-registry.json，填入你验证过的 provider

python scripts/validate_project.py ./explainers/caches/project.json
python scripts/validate_storyboard.py ./explainers/caches/storyboard.json
python scripts/preflight_model.py ./explainers/caches/project.json --registry model-registry.json
```

## 示例

| 示例 | 渲染器 | 说明 |
| --- | --- | --- |
| [`transformer`](examples/transformer/) | HyperFrames | 107.9 秒中文 Transformer 介绍，浅色学术风 |

[![Transformer preview](examples/transformer/preview.gif)](examples/transformer/)

```bash
python scripts/validate_examples.py
```

## 安装为技能

保持文件夹名为 `explain-anything`，根目录有 `SKILL.md`。

```bash
mkdir -p ~/.claude/skills
cp -r explain-anything ~/.claude/skills/explain-anything

# 或
npx skills add Temp0jd/explain-anything
```

## 设计原则

1. **理解为上**：只在概念需要时，才爬升到更复杂的产物。
2. **先来源，后文字**：每个主张先有锚点，再写句子。
3. **先形象，后字幕**：视频先找到具体主体，再写文案。
4. **让动词发生**：说“砍”，画面就真的砍。
5. **一个世界，一个含义**：配色、尺度、道具全片一致。
6. **先试片，再铺全片**：一镜或 30 秒过了，再规模化。
7. **模型可换，契约不换**：记录选择，不静默切换。
8. **漂亮但歪曲原意的产物，不如一段正确但朴素的文字。**

## 校验

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/validate_examples.py
python scripts/check_artifact.py --kind dir examples/transformer
python scripts/preflight_model.py examples/transformer/project.json --registry assets/model-registry.example.json
python scripts/qa_video.py examples/transformer/render/final.mp4 --project transformer-example \
  --storyboard examples/transformer/storyboard.json --captions examples/transformer/captions.srt --require-audio
python scripts/check_release.py
```

## 许可与致谢

MIT。见 `LICENSE`。灵感来源与第三方许可见 `NOTICE.md`：

- `vibe-knowledge-film`（MIT）：视觉先行知识短片流程
- `HyperFrames`（Apache-2.0）：HTML/CSS/GSAP 渲染
- `Manim Community`（MIT）：数学动画
