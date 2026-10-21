# Transformer · 旁白

Voice: zh-CN-XiaoxiaoNeural · rate +0% · pitch +0Hz

## Scene 01 · hook

Transformer 的核心，不是更深的网络，而是一种更直接的连接：让句子里的每个词，同时看见所有其他词。

## Scene 02 · problem

在它之前，循环网络只能沿着序列一步一步读。前面的信息要经过很多步才能到达后面，长距离依赖很容易被稀释。

## Scene 03 · attention

自注意力换了一种做法。每个词生成三个向量：Query、Key、Value。Query 和所有 Key 做点积，得到相关性分数；softmax 归一化后，再用这些权重去加权 Value。于是每个词都能直接聚合全句的信息。

## Scene 04 · heads

一个注意力头只能看一种关系。多头注意力让多个头并行，各自关注不同的模式：语法、指代、语义。最后把结果拼接起来，再投影回模型维度。

## Scene 05 · position

但注意力本身没有顺序感。打乱词序，分数可能一样。所以 Transformer 会给每个位置加上位置编码，让模型知道谁在前、谁在后。

## Scene 06 · block

一个 Transformer 层，通常是自注意力加前馈网络，再配合残差连接和层归一化。这样的层堆叠很多次，就形成了可以并行训练、容量很大的模型。

## Scene 07 · recap

所以，Transformer 的关键词是：直接连接、并行计算、多头视角、位置编码。它也有代价：注意力计算随序列长度平方增长。但它仍然是今天大语言模型的基础。
