---
type: wiki
created: 2026-02-12
area: "[[AI_ML]]"
tags: [langchain, retrieval, rag, ai, llm, vector-database]
---

# LangChain Retrieval

Retrieval（检索）是 LangChain 中实现 [[RAG-技术概述|RAG]]（Retrieval-Augmented Generation，检索增强生成）的核心组件，让 LLM 能够访问外部数据源。

## 什么是 RAG

RAG 结合了：
- **检索（Retrieval）**：从外部数据源查找相关信息
- **生成（Generation）**：基于检索到的信息生成回答

```
用户问题 → 检索相关文档 → 结合上下文 → LLM生成回答
```

## 核心组件

### 1. Document Loaders（文档加载器）

加载各种格式的文档：

```python
from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    UnstructuredHTMLLoader
)

# 文本文件
text_loader = TextLoader("document.txt")
text_docs = text_loader.load()

# PDF
pdf_loader = PyPDFLoader("document.pdf")
pdf_docs = pdf_loader.load()

# 网页
from langchain.document_loaders import WebBaseLoader
web_loader = WebBaseLoader("https://example.com")
web_docs = web_loader.load()
```

### 2. Text Splitters（文本分割器）

将长文档分割成适当大小的块：

```python
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter
)

# 按字符分割
splitter = CharacterTextSplitter(
    separator="\n",        # 分隔符
    chunk_size=1000,       # 每块大小
    chunk_overlap=200      # 重叠大小（保持上下文连贯）
)

# 递归分割（推荐）
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

docs = splitter.split_documents(pdf_docs)
```

**分割策略选择**：
- **代码**：按函数/类分割
- **Markdown**：按标题分割
- **一般文本**：递归字符分割

### 3. Embeddings（嵌入模型）

将文本转换为向量：

```python
from langchain.embeddings import (
    OpenAIEmbeddings,
    HuggingFaceEmbeddings,
    SentenceTransformerEmbeddings
)

# OpenAI
openai_embeddings = OpenAIEmbeddings()

# 开源替代
hf_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 生成向量
text = "This is a sample text"
vector = openai_embeddings.embed_query(text)
# 返回: [0.1, -0.2, 0.3, ...] 高维向量
```

### 4. Vector Stores（向量存储）

存储和检索向量化的文档：

#### FAISS（本地、免费）
```python
from langchain.vectorstores import FAISS

vectorstore = FAISS.from_documents(docs, openai_embeddings)

# 相似度搜索
results = vectorstore.similarity_search("query", k=3)

# 保存到磁盘
vectorstore.save_local("faiss_index")

# 加载
vectorstore = FAISS.load_local("faiss_index", openai_embeddings)
```

#### Chroma（本地、易用）
```python
from langchain.vectorstores import Chroma

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=openai_embeddings,
    persist_directory="./chroma_db"
)

# 持久化
vectorstore.persist()
```

#### Pinecone（云端、生产级）
```python
from langchain.vectorstores import Pinecone
import pinecone

pinecone.init(api_key="your-key", environment="us-west1-gcp")

vectorstore = Pinecone.from_documents(
    docs,
    openai_embeddings,
    index_name="my-index"
)
```

### 5. Retrievers（检索器）

从向量存储中检索文档：

```python
# 基础检索器
retriever = vectorstore.as_retriever()

# 配置检索参数
retriever = vectorstore.as_retriever(
    search_type="similarity",      # 或 "mmr"（最大边际相关性）
    search_kwargs={"k": 5}         # 返回文档数
)

# MMR 检索（平衡相关性和多样性）
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "lambda_mult": 0.5}
)

# 检索
docs = retriever.get_relevant_documents("query")
```

## 构建 RAG 系统

### 完整示例

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# 1. 加载文档
loader = TextLoader("knowledge_base.txt")
documents = loader.load()

# 2. 分割文本
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(documents)

# 3. 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# 4. 创建检索链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4", temperature=0),
    chain_type="stuff",              # 或 "map_reduce", "refine"
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True     # 返回引用的文档
)

# 5. 查询
query = "什么是LangChain的主要特点？"
result = qa_chain({"query": query})

print(f"答案: {result['result']}")
print(f"来源: {result['source_documents']}")
```

### Chain Types

- **stuff**：将所有文档填入一个提示词（简单、快速）
- **map_reduce**：分别处理每个文档，再汇总（适合多文档）
- **refine**：迭代式精化答案（适合长文档）
- **map_rerank**：对每个文档生成答案并打分，选最高分（适合问答）

## 高级检索技术

### 1. Multi-Query Retrieval

生成多个查询变体，提高召回率：

```python
from langchain.retrievers import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=ChatOpenAI(temperature=0)
)
```

### 2. Contextual Compression

压缩检索结果，只保留最相关部分：

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever()
)
```

### 3. Ensemble Retrieval

组合多个检索器：

```python
from langchain.retrievers import EnsembleRetriever

ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever],
    weights=[0.5, 0.5]
)
```

### 4. Parent Document Retrieval

检索小块但返回大块（保持上下文）：

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
```

## 评估 RAG 系统

### 检索质量

```python
from langchain.evaluation import load_evaluator

evaluator = load_evaluator("context_qa")

# 评估回答质量
result = evaluator.evaluate_strings(
    prediction="预测的答案",
    reference="标准答案",
    input="问题"
)
```

### 关键指标

1. **召回率（Recall）**：相关文档被检索的比例
2. **精确率（Precision）**：检索文档中相关的比例
3. **MRR（Mean Reciprocal Rank）**：第一个相关文档的排名倒数
4. **NDCG（Normalized Discounted Cumulative Gain）**：考虑排序质量的指标

## 最佳实践

### 1. 文本分割

- **大小选择**：通常 500-1000 tokens
- **重叠设置**：10-20% 的块大小
- **根据内容调整**：代码块保持函数完整性，文章保持段落完整性

### 2. 嵌入模型选择

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 通用 | text-embedding-ada-002 | 性能好、成本低 |
| 中文 | BGE-large-zh | 针对中文优化 |
| 代码 | code-embeddings | 理解代码语义 |
| 轻量级 | all-MiniLM-L6-v2 | 本地运行、免费 |

### 3. 向量存储选择

- **开发测试**：FAISS、Chroma（本地、免费）
- **生产环境**：Pinecone、Weaviate（云端、高可用）
- **大规模数据**：Milvus、Pgvector（企业级）

### 4. 元数据过滤

```python
# 添加元数据
docs = [
    Document(
        page_content="内容",
        metadata={"source": "doc1.pdf", "category": "tech", "date": "2024-01-01"}
    )
]

# 过滤检索
results = vectorstore.similarity_search(
    "query",
    filter={"category": "tech"}
)
```

## 常见陷阱

### 1. 块大小不当

**问题**：块太大导致检索不精确，太小丢失上下文。

**解决**：
- 根据问题复杂度调整块大小
- 使用重叠保持上下文
- 考虑使用 Parent Document Retrieval

### 2. 嵌入模型不匹配

**问题**：中英文混合内容使用纯英文嵌入模型效果差。

**解决**：
- 多语言内容使用多语言嵌入模型
- 专业领域使用领域特化模型

### 3. 检索参数不调优

**问题**：k 值太小遗漏重要信息，太大引入噪声。

**解决**：
- 根据数据集大小调整 k 值（通常 3-10）
- 使用 MMR 平衡相关性和多样性
- 设置相似度阈值过滤低质量结果

### 4. 忽视元数据

**问题**：检索结果包含过时或无关的文档。

**解决**：
- 添加时间戳、类别等元数据
- 使用元数据过滤
- 定期更新向量存储

## 与现有 RAG 知识关联

LangChain 的 Retrieval 组件实现了 [[RAG-技术概述|RAG 架构]] 中的核心环节：

1. **数据预处理**：Document Loaders + Text Splitters 对应 [[RAG-数据预处理与索引|数据预处理]]
2. **索引构建**：Vector Stores 对应 [[RAG-数据预处理与索引|索引构建]]
3. **检索**：Retrievers 对应 [[RAG-实时检索与重排序|检索与重排序]]
4. **上下文构建**：Chain Types 对应 [[RAG-上下文构建与生成|上下文构建]]

## 相关概念

- [[RAG-技术概述]] - RAG 技术全景
- [[LangChain-Chains]] - 构建 RAG 链
- [[LangChain-Agents]] - 结合检索的智能代理
- [[FAISS]] - Facebook AI Similarity Search
- [[Pinecone]] - 托管向量数据库
- [[Chroma]] - 开源向量数据库
