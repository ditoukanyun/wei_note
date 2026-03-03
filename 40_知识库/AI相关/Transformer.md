---
created: 2025-03-02
area: "[[AI相关]]"
tags: [ai, llm, deep-learning, transformer]
---

# Transformer

## 定义

Transformer是一种基于**自注意力机制（Self-Attention）**的神经网络架构，2017年由Google提出（论文《Attention Is All You Need》）。它是现代大语言模型（LLM）的基础架构，彻底改变了自然语言处理领域。

## 核心创新

**传统序列模型的问题**：

- RNN/LSTM：串行计算，难以并行；长距离依赖困难
- CNN：局部感受野，捕捉长距离依赖需要很多层

**Transformer的解决方案**：

- **完全基于注意力机制**：无需递归，完全并行
- **自注意力**：直接建模序列中任意两个位置的关系
- **位置编码**：显式注入位置信息

## 整体架构

```
输入 → [Embedding + Positional Encoding] →
      [Encoder × N] → [Decoder × N] → 输出
```

**Encoder（编码器）**：理解输入
**Decoder（解码器）**：生成输出

## 核心组件

### 1. 自注意力机制（Self-Attention）

**核心思想**：每个位置的表示都是所有位置的加权平均，权重由注意力计算决定。

```python
def self_attention(Q, K, V, mask=None):
    """
    Q: Query (batch, seq_len, d_k)
    K: Key   (batch, seq_len, d_k)
    V: Value (batch, seq_len, d_v)
    """
    # 1. 计算注意力分数
    scores = Q @ K.transpose(-2, -1) / sqrt(d_k)

    # 2. 应用mask（可选，用于Decoder的自回归）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -inf)

    # 3. Softmax归一化
    attention_weights = softmax(scores, dim=-1)

    # 4. 加权求和
    output = attention_weights @ V

    return output, attention_weights
```

**直观理解**：

- 读句子时，每个词都会"关注"其他词
- "它"会更多地关注"猫"而不是"跑"
- 注意力权重显示这种关注程度

### 2. 多头注意力（Multi-Head Attention）

**思想**：并行计算多组注意力，捕捉不同维度的关系。

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)

        # 线性投影并分头
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # 计算注意力
        attention_output, weights = self_attention(Q, K, V, mask)

        # 合并多头的结果
        attention_output = attention_output.transpose(1, 2).contiguous()
        attention_output = attention_output.view(batch_size, -1, self.d_k * self.num_heads)

        return self.W_o(attention_output)
```

### 3. 位置编码（Positional Encoding）

**问题**：Transformer没有递归，不知道词的位置

**解决方案**：显式添加位置信息

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()

        # 使用正弦/余弦函数
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()

        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() *
            -(math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

**特点**：

- 每个位置有唯一的编码
- 可以处理比训练时更长的序列
- 相对位置可以通过线性变换得到

### 4. 前馈网络（Feed-Forward Network）

```python
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)

    def forward(self, x):
        return self.linear2(F.relu(self.linear1(x)))
```

**作用**：为模型增加非线性表达能力

### 5. 层归一化（Layer Normalization）

```python
class LayerNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta
```

## 完整Encoder层

```python
class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # 自注意力子层
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))  # 残差连接

        # 前馈子层
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))  # 残差连接

        return x
```

## 完整Decoder层

```python
class TransformerDecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.masked_self_attn = MultiHeadAttention(d_model, num_heads)
        self.cross_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.norm3 = LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        # 带mask的自注意力（自回归）
        attn_output = self.masked_self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 交叉注意力（关注Encoder输出）
        attn_output = self.cross_attn(
            x, encoder_output, encoder_output, src_mask
        )
        x = self.norm2(x + self.dropout(attn_output))

        # 前馈
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_output))

        return x
```

## 为什么Transformer有效

### 1. 并行计算

**RNN**：必须按顺序计算

```
h1 → h2 → h3 → h4
```

**Transformer**：可以同时计算所有位置

```
h1   h2   h3   h4
 ↓    ↓    ↓    ↓
同时计算
```

### 2. 长距离依赖

**RNN**：信息需要一步步传递，容易丢失
**Transformer**：任意两个位置直接相连

```
"虽然...但是..."
在Transformer中："虽然"可以直接关注"但是"
```

### 3. 可解释性

注意力权重可以可视化，显示模型关注了哪些词。

## 从Transformer到GPT/BERT

| 模型                | 结构              | 训练目标              | 用途     |
| ------------------- | ----------------- | --------------------- | -------- |
| **原始Transformer** | Encoder + Decoder | 机器翻译              | 翻译任务 |
| **BERT**            | 仅Encoder         | Masked Language Model | 理解任务 |
| **GPT**             | 仅Decoder         | 自回归语言模型        | 生成任务 |
| **T5**              | Encoder-Decoder   | Span Corruption       | 通用任务 |

## 复杂度分析

| 模型            | 序列操作复杂度 | 每层复杂度  | 最大路径长度 |
| --------------- | -------------- | ----------- | ------------ |
| RNN             | O(n)           | O(n·d²)     | O(n)         |
| CNN             | O(1)           | O(k·n·d²)   | O(log_k(n))  |
| **Transformer** | **O(1)**       | **O(n²·d)** | **O(1)**     |

**注意**：Transformer的O(n²)复杂度在长序列时成为瓶颈，后续有了各种高效注意力变体（Linear Attention, Sparse Attention等）。

## 相关概念

- [[LLM]] - 基于Transformer的大语言模型
- [[AI Agent]] - 使用LLM作为推理引擎
- [[Attention Mechanism]] - 注意力机制
- [[BERT]] - 双向Transformer编码器
- [[GPT]] - 生成式预训练Transformer

## 关键论文

- _Attention Is All You Need_ (Vaswani et al., 2017) - Transformer原始论文
- _BERT: Pre-training of Deep Bidirectional Transformers_ (Devlin et al., 2018)
- _Improving Language Understanding by Generative Pre-Training_ (Radford et al., 2018) - GPT-1

## 学习建议

1. **必读论文**：《Attention Is All You Need》
2. **动手实现**：用PyTorch从零实现一个简化版Transformer
3. **可视化理解**：看注意力权重的可视化，理解模型在看什么
4. **对比学习**：对比RNN/LSTM和Transformer的差异
