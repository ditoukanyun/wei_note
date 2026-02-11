---
title: RAG数据预处理与索引
date: 2025-02-10
tags: [RAG, 数据预处理, 向量化, 索引, FAISS, 向量数据库]
category: 领域
status: active
parent: "[[MOC-RAG]]"
aliases: [RAG索引, 文档向量化, 向量数据库构建]
---

# RAG数据预处理与索引

> **父级**：[[MOC-RAG]]  
> **上级**：[[RAG-核心原理]]  
> **相关**：[[RAG-实时检索与重排序]], [[RAG-代码示例]]

## 阶段概述

数据预处理与索引是RAG系统的**离线准备阶段**，将原始文档转换为可高效检索的向量索引。

> [!info] 核心目标
> 将非结构化文本转换为结构化的向量表示，建立高效的相似度搜索索引。

```mermaid
graph LR
    A[原始文档] --> B[文档解析]
    B --> C[文本分块]
    C --> D[向量化]
    D --> E[索引构建]
    E --> F[向量数据库]
```

## 1. 文档解析

### 支持的文档格式

| 格式 | 工具库 | 说明 |
|------|--------|------|
| **PDF** | PyPDF2、pdfplumber | 学术论文、报告 |
| **Word** | python-docx | 合同、文档 |
| **Markdown** | 原生支持 | 技术文档、笔记 |
| **HTML** | BeautifulSoup | 网页内容 |
| **CSV/Excel** | pandas | 结构化数据 |

### 解析示例

```python
# PDF解析
import pdfplumber

def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text
```

## 2. 文本分块（Chunking）

### 为什么需要分块？

- **上下文限制**：LLM有最大输入长度限制
- **检索精度**：小块文本更精准匹配查询
- **噪声控制**：避免无关信息干扰

### 分块策略对比

| 策略 | 方法 | 优点 | 缺点 |
|------|------|------|------|
| **固定长度** | 按字符/Token数切分 | 简单、均匀 | 可能切断语义 |
| **递归分块** | 按段落→句子逐层切分 | 保持结构 | 实现复杂 |
| **语义分块** | 基于语义相似度切分 | 语义完整 | 计算成本高 |
| **文档结构** | 按标题、章节切分 | 逻辑清晰 | 依赖格式 |

### 分块参数

> [!tip] 最佳实践
> - **块大小**：200-500 tokens（根据嵌入模型调整）
> - **重叠度**：10-20%（保持上下文连贯性）
> - **最大块数**：根据索引容量和查询延迟权衡

### 代码实现

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 递归分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块500字符
    chunk_overlap=50,      # 重叠50字符
    separators=["\n\n", "\n", "。", "！", "？"]
)

chunks = text_splitter.split_text(long_document)
```

## 3. 向量化（Embedding）

### 嵌入模型选择

| 模型 | 维度 | 语言 | 特点 |
|------|------|------|------|
| **text-embedding-ada-002** | 1536 | 多语言 | OpenAI，效果稳定 |
| **bge-large-zh** | 1024 | 中文 | BAAI，中文优化 |
| **m3e-base** | 768 | 中文 | 轻量，开源 |
| **gte-large** | 1024 | 多语言 | 阿里，高性能 |
| **E5** | 1024 | 多语言 | 微软，指令优化 |

### 向量化流程

```mermaid
graph LR
    A[文本块] --> B[嵌入模型]
    B --> C[向量表示]
    C --> D[归一化]
    D --> E[存储]
```

### 代码示例

```python
from sentence_transformers import SentenceTransformer

# 加载嵌入模型
encoder = SentenceTransformer('BAAI/bge-large-zh')

# 文档向量化
documents = ["大模型原理...", "RAG技术优点...", ...]
embeddings = encoder.encode(documents, normalize_embeddings=True)

print(f"向量维度: {embeddings.shape}")
# 输出: (文档数, 1024)
```

### 向量归一化

```python
import numpy as np

# L2归一化
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# 归一化后，余弦相似度 = 向量点积
similarity = np.dot(query_vec, doc_vec)
```

## 4. 索引构建

### 索引类型

| 类型 | 算法 | 特点 | 适用场景 |
|------|------|------|----------|
| **Flat** | 暴力搜索 | 精确、慢 | 小规模(<10k) |
| **IVF** | 倒排文件 | 平衡 | 中等规模 |
| **HNSW** | 图索引 | 快速、近似 | 大规模 |
| **PQ** | 乘积量化 | 压缩存储 | 内存受限 |

### FAISS索引示例

```python
import faiss
import numpy as np

# 准备数据
dim = embeddings.shape[1]  # 向量维度

# 1. 创建Flat索引（精确搜索）
index_flat = faiss.IndexFlatL2(dim)
index_flat.add(embeddings)

# 2. 创建HNSW索引（快速近似搜索）
index_hnsw = faiss.IndexHNSWFlat(dim, 32)
index_hnsw.hnsw.efConstruction = 200
index_hnsw.add(embeddings)

# 3. 创建IVF索引（倒排文件）
nlist = 100  # 聚类中心数
quantizer = faiss.IndexFlatL2(dim)
index_ivf = faiss.IndexIVFFlat(quantizer, dim, nlist)
index_ivf.train(embeddings)
index_ivf.add(embeddings)

# 保存索引
faiss.write_index(index_flat, "rag_index.faiss")
```

## 5. 元数据管理

### 为什么需要元数据？

- **来源追溯**：知道答案来自哪篇文档
- **过滤检索**：按时间、类别等条件筛选
- **展示信息**：显示标题、作者、日期等

### 元数据结构

```python
metadata = {
    "doc_id": "doc_001",
    "title": "RAG技术白皮书",
    "source": "企业内部文档",
    "author": "技术团队",
    "created_at": "2024-01-15",
    "category": "技术文档",
    "page": 12,
    "chunk_index": 3
}
```

### 存储方案

```python
# 方案1：FAISS + 元数据字典
index = faiss.IndexFlatL2(dim)
index.add(embeddings)
metadata_list = [metadata1, metadata2, ...]  # 按相同顺序存储

# 方案2：使用向量数据库（自带元数据）
import chromadb
client = chromadb.Client()
collection = client.create_collection("rag_docs")
collection.add(
    embeddings=embeddings.tolist(),
    documents=chunks,
    metadatas=metadata_list,
    ids=[f"doc_{i}" for i in range(len(chunks))]
)
```

## 6. 完整流程代码

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGIndexer:
    def __init__(self, model_name='BAAI/bge-large-zh'):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []
    
    def add_documents(self, docs, metadatas=None):
        """添加文档到索引"""
        self.documents.extend(docs)
        if metadatas:
            self.metadata.extend(metadatas)
        
        # 向量化
        embeddings = self.encoder.encode(docs)
        
        # 构建或更新索引
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        
        self.index.add(embeddings)
    
    def save(self, index_path, docs_path):
        """保存索引和文档"""
        faiss.write_index(self.index, index_path)
        import pickle
        with open(docs_path, 'wb') as f:
            pickle.dump({'docs': self.documents, 'meta': self.metadata}, f)
    
    def load(self, index_path, docs_path):
        """加载索引和文档"""
        self.index = faiss.read_index(index_path)
        import pickle
        with open(docs_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['docs']
            self.metadata = data['meta']

# 使用示例
indexer = RAGIndexer()
docs = ["RAG是一种增强LLM的技术", "向量数据库用于存储嵌入"]
indexer.add_documents(docs)
indexer.save("index.faiss", "docs.pkl")
```

## 常见问题

> [!question] Q: 分块大小如何选择？
> A: 一般200-500 tokens，根据文档类型调整。技术文档可以大一些（500），FAQ可以小一些（200）。

> [!question] Q: 如何更新索引？
> A: 增量更新时，只需向量化新文档并调用`index.add()`。FAISS支持增量添加。

> [!question] Q: 向量维度对性能的影响？
> A: 维度越高，存储和计算成本越大。但过低维度可能影响语义表达能力。一般768-1536是较好的平衡点。

## 相关笔记

- [[RAG-核心原理]] - 整体架构
- [[RAG-实时检索与重排序]] - 下一阶段
- [[RAG-代码示例]] - 完整代码实现

## 参考资料

- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers文档](https://www.sbert.net/)
- [原文：RAG技术深度解析](https://juejin.cn/post/7501543492502683700)