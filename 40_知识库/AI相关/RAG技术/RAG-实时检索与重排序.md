---
title: RAG实时检索与重排序
date: 2025-02-10
tags: [RAG, 检索, 重排序, Top-K, 相似度搜索, 向量检索]
category: 领域
status: active
parent: "[[MOC-RAG]]"
aliases: [RAG检索, 向量搜索, Rerank]
---

# RAG实时检索与重排序

> **父级**：[[MOC-RAG]]  
> **上级**：[[RAG-核心原理]]  
> **相关**：[[RAG-数据预处理与索引]], [[RAG-上下文构建与生成]]

## 阶段概述

实时检索与重排序是RAG系统的**在线查询阶段**，根据用户问题实时检索最相关的文档片段。

> [!info] 核心目标
> 在海量文档中快速、准确地找到与用户查询最相关的Top-K片段。

```mermaid
graph LR
    A[用户查询] --> B[Query向量化]
    B --> C[向量检索]
    C --> D[Top-K初筛]
    D --> E[重排序优化]
    E --> F[返回结果]
```

## 1. Query向量化

### 查询编码

用户提问需要经过与文档相同的嵌入模型转换为向量：

```python
def encode_query(query, encoder):
    """将查询转换为向量"""
    query_embedding = encoder.encode([query])
    return query_embedding

# 示例
query = "如何提高RAG的准确性？"
query_vec = encode_query(query, encoder)
```

### 查询预处理

```python
import re

def preprocess_query(query):
    """查询预处理"""
    # 去除多余空格
    query = re.sub(r'\s+', ' ', query.strip())
    # 去除特殊字符
    query = re.sub(r'[^\w\s\u4e00-\u9fff]', '', query)
    return query
```

## 2. 向量检索

### 相似度度量

| 度量方法 | 公式 | 特点 | 适用场景 |
|---------|------|------|----------|
| **余弦相似度** | $\cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$ | 忽略向量长度 | 文本语义匹配 |
| **欧氏距离** | $d = \sqrt{\sum(A_i - B_i)^2}$ | 考虑绝对距离 | 空间位置敏感 |
| **点积** | $A \cdot B$ | 计算快速 | 归一化向量 |

### FAISS检索实现

```python
import faiss
import numpy as np

def retrieve_faiss(query_embedding, index, k=5):
    """
    使用FAISS进行向量检索
    
    Args:
        query_embedding: 查询向量 (1, dim)
        index: FAISS索引对象
        k: 返回Top-K个结果
    
    Returns:
        distances: 距离数组
        indices: 文档索引数组
    """
    distances, indices = index.search(query_embedding, k)
    return distances[0], indices[0]

# 示例
query = "RAG优化方法"
query_emb = encoder.encode([query])
distances, indices = retrieve_faiss(query_emb, index, k=5)

# 获取对应文档
results = [documents[i] for i in indices]
```

### 检索参数调优

```python
# HNSW索引参数调优
index = faiss.IndexHNSWFlat(dim, 32)  # 32邻居
index.hnsw.efConstruction = 200         # 构建时搜索深度
index.hnsw.efSearch = 128               # 查询时搜索深度

# efSearch越大，精度越高，速度越慢
```

## 3. Top-K筛选

### K值选择

> [!tip] 经验法则
> - **K=3-5**：适用于简单问答，上下文较短
> - **K=10-20**：适用于复杂查询，需要综合信息
> - **自适应K**：根据查询复杂度动态调整

### 过滤策略

```python
def filter_by_threshold(distances, indices, threshold=0.7):
    """根据相似度阈值过滤"""
    filtered = []
    for dist, idx in zip(distances, indices):
        # 对于余弦相似度，距离越小越相似（如果是L2）
        # 这里假设已转换为相似度分数
        similarity = 1 - dist  # L2距离转相似度简化示例
        if similarity > threshold:
            filtered.append((idx, similarity))
    return filtered
```

## 4. 重排序（Reranking）

### 为什么需要重排序？

- **向量检索局限**：双编码器（bi-encoder）独立编码，可能丢失交互信息
- **精度提升**：交叉编码器（cross-encoder）联合编码，精度更高
- **重排序流程**：先用快速模型召回候选，再用精确模型精排

### 双编码器 vs 交叉编码器

```
双编码器（Bi-Encoder）：
查询 → [Encoder] → 向量 ─┐
                        ├→ 相似度计算 → 排序
文档 → [Encoder] → 向量 ─┘
特点：速度快，适合大规模检索

交叉编码器（Cross-Encoder）：
[查询, 文档] → [Joint Encoder] → 相关度分数
特点：精度高，适合小规模精排
```

### 重排序实现

```python
from sentence_transformers import CrossEncoder

# 加载重排序模型
reranker = CrossEncoder('BAAI/bge-reranker-large')

def rerank_documents(query, documents, top_k=5):
    """
    对检索结果进行重排序
    
    Args:
        query: 用户查询
        documents: 初步检索的文档列表
        top_k: 最终返回数量
    
    Returns:
        重排序后的文档列表
    """
    # 构建查询-文档对
    pairs = [[query, doc] for doc in documents]
    
    # 计算相关度分数
    scores = reranker.predict(pairs)
    
    # 按分数排序
    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    # 返回Top-K
    return [doc for doc, score in scored_docs[:top_k]]
```

### 完整检索流程

```python
class RAGRetriever:
    def __init__(self, encoder, index, documents):
        self.encoder = encoder
        self.index = index
        self.documents = documents
        self.reranker = CrossEncoder('BAAI/bge-reranker-large')
    
    def retrieve(self, query, k_retrieve=20, k_final=5):
        """
        两阶段检索：召回 + 精排
        """
        # 阶段1：向量检索召回候选
        query_emb = self.encoder.encode([query])
        distances, indices = self.index.search(query_emb, k_retrieve)
        
        candidates = [self.documents[i] for i in indices[0]]
        
        # 阶段2：重排序精选
        if len(candidates) > k_final:
            final_results = rerank_documents(query, candidates, k_final)
        else:
            final_results = candidates
        
        return final_results
```

## 5. 混合检索

### 向量 + 关键词混合

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    def __init__(self, documents, encoder, index):
        self.documents = documents
        self.encoder = encoder
        self.index = index
        
        # 初始化BM25
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def hybrid_search(self, query, alpha=0.5, k=5):
        """
        混合检索：向量相似度 + BM25关键词匹配
        
        Args:
            alpha: 向量检索权重 (0-1)
        """
        # 向量检索
        query_emb = self.encoder.encode([query])
        _, vec_indices = self.index.search(query_emb, k*2)
        
        # BM25检索
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_topk = np.argsort(bm25_scores)[-k*2:][::-1]
        
        # 融合两种检索结果
        all_candidates = set(vec_indices[0]) | set(bm25_topk)
        
        # 计算融合分数
        final_scores = []
        for idx in all_candidates:
            vec_score = 1.0 if idx in vec_indices[0] else 0.0
            bm25_score = bm25_scores[idx] / max(bm25_scores) if max(bm25_scores) > 0 else 0
            
            fused_score = alpha * vec_score + (1 - alpha) * bm25_score
            final_scores.append((idx, fused_score))
        
        # 排序返回Top-K
        final_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in final_scores[:k]]
        
        return [self.documents[i] for i in top_indices]
```

## 6. 性能优化

### 索引优化

```python
# 使用GPU加速
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)

# 使用量化加速
index = faiss.IndexIVFPQ(quantizer, dim, nlist, m, 8)
```

### 缓存策略

```python
import functools

@functools.lru_cache(maxsize=1000)
def cached_encode(query):
    """缓存查询向量"""
    return encoder.encode([query])
```

## 常见问题

> [!question] Q: 检索结果不相关怎么办？
> A: 1) 检查嵌入模型是否适合领域 2) 调整分块策略 3) 使用重排序 4) 增加混合检索

> [!question] Q: 如何提高检索速度？
> A: 1) 使用HNSW等近似索引 2) 使用GPU加速 3) 减少向量维度 4) 增加缓存

> [!question] Q: 重排序会增加多少延迟？
> A: 交叉编码器比双编码器慢10-100倍，建议只对Top-20候选重排序。

## 相关笔记

- [[RAG-核心原理]] - 整体架构
- [[RAG-数据预处理与索引]] - 上一阶段
- [[RAG-上下文构建与生成]] - 下一阶段
- [[RAG-代码示例]] - 完整代码实现

## 参考资料

- [FAISS Tutorial](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [Sentence-Transformers Cross-Encoder](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- [原文：RAG技术深度解析](https://juejin.cn/post/7501543492502683700)