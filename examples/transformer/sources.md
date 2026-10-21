# Sources and claim ledger

The video is an introductory visual explanation. It follows the original Transformer paper for the mechanism and marks broad claims as inference.

| # | Claim | Source anchor | Type | Confidence |
| --- | --- | --- | --- | --- |
| 1 | Self-attention relates different positions in one sequence; each position produces Query, Key, and Value, and the output is a scaled dot-product attention over values. | Vaswani et al., *Attention Is All You Need* (2017), §3.2, Eq. (1) | fact | high |
| 2 | Multi-head attention runs several attention heads in parallel, concatenates their outputs, and projects the result. | Vaswani et al. (2017), §3.2.1 | fact | high |
| 3 | Positional encodings are added to token embeddings because the model contains no recurrence and no convolution, so it has no inherent notion of order. | Vaswani et al. (2017), §3.3 and §3.5 | fact | high |
| 4 | Each encoder/decoder sub-layer uses a residual connection followed by layer normalization. | Vaswani et al. (2017), §3.1 | fact | high |
| 5 | The position-wise feed-forward network is applied independently to each position. | Vaswani et al. (2017), §3.3 | fact | high |
| 6 | Self-attention has (O(n^2 d)) time/memory complexity in the sequence length and a path length of (O(1)) between any two positions; this is the source of the video's (O(n^2)) cost label. | Vaswani et al. (2017), §4, Table 1 | fact | high |
| 7 | The Transformer architecture relies solely on attention, without recurrence or convolution. | Vaswani et al. (2017), abstract | fact | high |
| 8 | The Transformer is a foundation of many modern large language models. | Broad consensus in the LLM literature; e.g. Zhao et al., *A Survey of Large Language Models* (arXiv:2303.18223) | inference | medium-high |
| 9 | The 5×5 attention matrix, the values in it, and the "O(n²)" label are illustrative teaching values, not measurements from a trained model. | This project's `storyboard.json` and source code | fact (about this video) | high |

## References

1. Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, and Illia Polosukhin. "Attention Is All You Need." NeurIPS 2017. arXiv:1706.03762. https://arxiv.org/abs/1706.03762
2. Jay Alammar. "The Illustrated Transformer." https://jalammar.github.io/illustrated-transformer/
3. Alexander M. Rush et al. "The Annotated Transformer." https://nlp.seas.harvard.edu/annotated-transformer/
4. Wayne Xin Zhao et al. "A Survey of Large Language Models." arXiv:2303.18223. https://arxiv.org/abs/2303.18223

## Notes

- The exact attention weights in the video are illustrative. A real model's weights depend on its parameters, input, and layer.
- The video shows one encoder-style layer for intuition; it does not cover decoder masking, cross-attention, training objectives, or specific LLM architectures.
- The (O(n^2)) label refers to the attention matrix over sequence length; optimized kernels and sparse/linear attention change the constant and, in some variants, the asymptotic cost.
