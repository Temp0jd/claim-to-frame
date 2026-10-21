# Transformer — storyboard

**Thesis:** Transformer 的核心不是更深的网络，而是让每个词直接看见所有词的自注意力机制。  
**Duration:** 107.9 s  
**Renderer:** HyperFrames 0.8.181  
**Style:** warm paper, terracotta accent, serif display, 96 px safe margins.

| ID | Time | Purpose | Caption | Visual | Action | Small text | Audio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | 0.0–10.7 | hook | Transformer 的核心，不是更深的网络，而是更直接的连接。 | 五个中文词卡错落排布；弧线从「猫」连向其他词。 | 标题与词卡浮现；弧线展开。 | Transformer；SELF-ATTENTION · 2017 | 让每个词，同时看见所有其他词。 |
| S02 | 10.7–23.6 | example | 循环网络只能一步一步读，长距离信息容易被稀释。 | 英文词卡沿箭头排成链；赭色圆点沿链移动；底部渐隐线。 | 圆点移动；渐隐线与警示出现。 | THE OLD WAY；顺序执行 / 难以并行 | 前面的信息要经过很多步才能到达后面。 |
| S03 | 23.6–44.5 | mechanism | 每个词生成 Q、K、V；Query 与所有 Key 做点积，softmax 后加权 Value。 | 「猫」与 Q/K/V；5×5 相关性矩阵；右侧加权输出。 | Q/K/V 出现；矩阵填充；第一行高亮；公式与输出浮现。 | Q · Kᵀ → SOFTMAX；Attention(Q,K,V)=softmax(QKᵀ/√d_k)V | 每个词直接聚合全句的信息。 |
| S04 | 44.5–60.2 | mechanism | 多头注意力并行关注不同关系，再拼接投影。 | 四张 HEAD 卡片（语法、指代、语义、局部）；concat 与 W_O。 | 头卡依次出现；合并与投影出现。 | MULTI-HEAD ATTENTION；HEAD 01–04 | 每个头有自己的 Q/K/V 投影。 |
| S05 | 60.2–74.7 | mechanism | 注意力没有顺序感；位置编码把顺序信息加回来。 | 五个词卡错位再归位；位置编号；sin/cos 波形与公式。 | 词卡错位、归位；编号与波形出现。 | POSITIONAL ENCODING；1 2 3 4 5 | 让模型知道谁在前、谁在后。 |
| S06 | 74.7–90.4 | mechanism | 一个 Transformer 层由多头注意力、前馈网络、残差连接和层归一化组成。 | 纵向层结构：输入 → Attention → Add & Norm → FFN → Add & Norm → 输出；右侧 ×N。 | 模块从上到下点亮；残差与 ×N 出现。 | THE TRANSFORMER BLOCK；× N | 层堆叠很多次，形成大容量模型。 |
| S07 | 90.4–107.9 | recap | 直接连接、并行、多头、位置编码；代价是 O(n²) 的注意力。 | 四张关键词卡片；O(n²) 成本；结尾卡与论文引用。 | 卡片出现；成本出现；结尾卡覆盖并停留。 | WHY IT MATTERS；O(n²)；Attention Is All You Need · 2017 | 它仍然是今天大语言模型的基础。 |

## Notes

- The 5×5 weights are illustrative.
- The video is an introduction; it omits decoder masking, cross-attention, training objectives, and specific LLM architectures.
- The ending returns to the opening claim: direct connection between tokens.
