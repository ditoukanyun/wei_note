---
title: RAG代码示例合集
date: 2025-02-10
tags: [RAG, 代码示例, Python, 实战, FAISS, LLM]
category: 领域
status: active
parent: "[[MOC-RAG]]"
aliases: [RAG代码, RAG实现, RAG实战]
---

# RAG代码示例合集

> **父级**：[[MOC-RAG]]  
> **上级**：[[RAG-核心原理]]  
> **相关**：[[RAG-数据预处理与索引]], [[RAG-实时检索与重排序]], [[RAG-上下文构建与生成]]

## 环境准备

### 依赖安装

```bash
pip install sentence-transformers faiss-cpu transformers
pip install langchain openai
pip install numpy pandas
```

## 1. 基础RAG实现

### 完整流程代码

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class SimpleRAG:
    """
    简化版RAG实现
    """
    def __init__(self, embedding_model='all-MiniLM-L6-v2', llm_model='gpt2'):
        # 初始化嵌入模型
        self.encoder = SentenceTransformer(embedding_model)
        
        # 初始化生成模型
        self.generator = pipeline("text-generation", model=llm_model)
        
        # 向量索引
        self.index = None
        self.documents = []
    
    def add_documents(self, documents):
        """
        添加文档到知识库
        
        Args:
            documents: 文档字符串列表
        """
        self.documents = documents
        
        # 向量化
        print("正在编码文档...")
        embeddings = self.encoder.encode(documents)
        
        # 创建FAISS索引
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        
        print(f"已添加 {len(documents)} 个文档")
    
    def retrieve(self, query, k=5):
        """
        检索相关文档
        
        Args:
            query: 查询字符串
            k: 返回Top-K个结果
        
        Returns:
            相关文档列表
        """
        # 查询向量化
        query_embedding = self.encoder.encode([query])
        
        # 检索
        distances, indices = self.index.search(query_embedding, k)
        
        # 返回文档
        results = [self.documents[i] for i in indices[0]]
        return results
    
    def generate(self, query, contexts):
        """
        基于上下文生成回答
        
        Args:
            query: 用户问题
            contexts: 检索到的上下文
        
        Returns:
            生成的回答
        """
        # 构建提示
        context_text = "\n".join([f"{i+1}. {ctx}" for i, ctx in enumerate(contexts)])
        
        prompt = f"""基于以下信息回答问题：

{context_text}

问题：{query}
答案："""
        
        # 生成
        response = self.generator(
            prompt,
            max_length=500,
            temperature=0.7,
            do_sample=True
        )
        
        return response[0]['generated_text']
    
    def query(self, question, k=5):
        """
        完整RAG查询流程
        
        Args:
            question: 用户问题
            k: 检索文档数量
        
        Returns:
            回答和引用的文档
        """
        # 1. 检索
        contexts = self.retrieve(question, k=k)
        
        # 2. 生成
        answer = self.generate(question, contexts)
        
        return {
            'query': question,
            'answer': answer,
            'contexts': contexts
        }

# 使用示例
if __name__ == "__main__":
    # 初始化RAG
    rag = SimpleRAG()
    
    # 添加文档
    docs = [
        "大语言模型（LLM）是一种基于深度学习的自然语言处理模型。",
        "RAG技术通过检索外部知识来增强大模型的生成能力。",
        "向量数据库用于存储和检索高维向量数据。",
        "FAISS是Facebook开发的快速相似度搜索库。",
        "嵌入模型将文本转换为向量表示。"
    ]
    rag.add_documents(docs)
    
    # 查询
    result = rag.query("什么是RAG技术？")
    print(f"问题：{result['query']}")
    print(f"回答：{result['answer']}")
    print(f"参考文档：{result['contexts']}")
```

## 2. 高级RAG实现

### 带重排序的RAG

```python
from sentence_transformers import CrossEncoder

class AdvancedRAG(SimpleRAG):
    """
    高级RAG：带重排序功能
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 加载重排序模型
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    def retrieve_with_rerank(self, query, k_retrieve=20, k_final=5):
        """
        两阶段检索：向量检索 + 交叉编码器重排序
        """
        # 阶段1：向量检索召回候选
        candidates = self.retrieve(query, k=k_retrieve)
        
        # 阶段2：重排序
        pairs = [[query, doc] for doc in candidates]
        scores = self.reranker.predict(pairs)
        
        # 按分数排序
        scored_candidates = list(zip(candidates, scores))
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 返回Top-K
        return [doc for doc, score in scored_candidates[:k_final]]
    
    def query(self, question, k=5):
        """使用重排序的查询"""
        # 使用重排序检索
        contexts = self.retrieve_with_rerank(question, k_final=k)
        
        # 生成
        answer = self.generate(question, contexts)
        
        return {
            'query': question,
            'answer': answer,
            'contexts': contexts
        }
```

### HyDE实现

```python
class HydeRAG(SimpleRAG):
    """
    HyDE (Hypothetical Document Embeddings) RAG实现
    """
    def retrieve_with_hyde(self, query, k=5):
        """
        使用HyDE进行检索
        """
        # 步骤1：生成假设答案
        hypo_prompt = f"简要回答以下问题：\n\n{query}\n\n简要回答："
        
        hypo_answer = self.generator(
            hypo_prompt,
            max_length=200,
            do_sample=True,
            temperature=0.7
        )[0]['generated_text']
        
        print(f"假设答案：{hypo_answer}")
        
        # 步骤2：用假设答案检索
        hypo_embedding = self.encoder.encode([hypo_answer])
        distances, indices = self.index.search(hypo_embedding, k)
        
        return [self.documents[i] for i in indices[0]]
```

## 3. 文本分块实现

```python
class TextChunker:
    """
    文本分块工具
    """
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_by_fixed_size(self, text):
        """固定长度分块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
        
        return chunks
    
    def split_by_sentences(self, text):
        """按句子分块"""
        import re
        sentences = re.split(r'(?<=[。！？])', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sent in sentences:
            if current_length + len(sent) > self.chunk_size:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [sent]
                current_length = len(sent)
            else:
                current_chunk.append(sent)
                current_length += len(sent)
        
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
    
    def split_recursive(self, text, separators=["\n\n", "\n", "。", "！", "？"]):
        """递归分块"""
        if len(text) <= self.chunk_size:
            return [text]
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                chunks = []
                current_chunk = ""
                
                for part in parts:
                    if len(current_chunk) + len(part) < self.chunk_size:
                        current_chunk += part + sep
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = part + sep
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                return chunks
        
        # 如果所有分隔符都不适用，使用固定长度
        return self.split_by_fixed_size(text)

# 使用示例
chunker = TextChunker(chunk_size=300, chunk_overlap=30)
text = "这是第一段。这是第二段！这是第三段？这是第四段。"
chunks = chunker.split_by_sentences(text)
print(chunks)
```

## 4. 提示模板集合

```python
class PromptTemplates:
    """
    RAG提示模板集合
    """
    
    @staticmethod
    def basic_rag(context, query):
        """基础RAG提示"""
        return f"""基于以下信息回答问题：

{context}

问题：{query}
答案："""
    
    @staticmethod
    def detailed_rag(context, query):
        """详细RAG提示"""
        return f"""你是一个专业的问答助手。请基于提供的参考信息回答用户问题。

## 参考信息
{context}

## 回答要求
1. 仅基于上述参考信息回答
2. 回答要准确、全面、简洁
3. 如果信息不足，请明确说明

## 用户问题
{query}

## 你的回答
"""
    
    @staticmethod
    def citation_rag(context, query):
        """带引用标注的提示"""
        return f"""基于以下参考信息回答问题，并在回答中标注信息来源。

参考信息：
{context}

回答格式要求：
- 使用[1]、[2]等标注引用来源
- 在回答末尾列出引用文档

问题：{query}

回答："""
    
    @staticmethod
    def step_by_step_rag(context, query):
        """分步推理提示"""
        return f"""基于以下信息，逐步分析问题并给出回答。

参考信息：
{context}

问题：{query}

请按以下步骤回答：
1. 分析问题关键点
2. 从参考信息中提取相关证据
3. 综合分析并得出结论

回答："""
```

## 5. 评估指标实现

```python
class RAGEvaluator:
    """
    RAG系统评估工具
    """
    
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """计算余弦相似度"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    @staticmethod
    def recall_at_k(retrieved, relevant, k):
        """
        计算Recall@K
        
        Args:
            retrieved: 检索到的文档ID列表
            relevant: 相关文档ID列表
            k: K值
        """
        retrieved_at_k = set(retrieved[:k])
        relevant_set = set(relevant)
        
        if not relevant_set:
            return 0.0
        
        return len(retrieved_at_k & relevant_set) / len(relevant_set)
    
    @staticmethod
    def mrr(retrieved, relevant):
        """
        计算Mean Reciprocal Rank
        """
        for rank, doc_id in enumerate(retrieved, 1):
            if doc_id in relevant:
                return 1.0 / rank
        return 0.0
    
    @staticmethod
    def faithfulness(answer, contexts):
        """
        评估回答的忠实度（简化版）
        
        检查回答中的信息是否都能在上下文中找到
        """
        import re
        
        # 提取回答中的关键句子
        sentences = re.split(r'(?<=[。！？])', answer)
        
        supported = 0
        for sent in sentences:
            if len(sent.strip()) < 5:
                continue
            
            # 检查是否在任一上下文中
            for ctx in contexts:
                if any(word in ctx for word in sent.strip().split()[:3]):
                    supported += 1
                    break
        
        return supported / len(sentences) if sentences else 0

# 评估示例
def evaluate_rag_system(rag_system, test_queries, ground_truth):
    """
    评估RAG系统性能
    """
    evaluator = RAGEvaluator()
    results = {
        'recall@5': [],
        'recall@10': [],
        'mrr': []
    }
    
    for query, truth in zip(test_queries, ground_truth):
        # 检索
        retrieved_docs = rag_system.retrieve(query, k=10)
        retrieved_ids = [doc['id'] for doc in retrieved_docs]
        
        # 计算指标
        results['recall@5'].append(evaluator.recall_at_k(retrieved_ids, truth, 5))
        results['recall@10'].append(evaluator.recall_at_k(retrieved_ids, truth, 10))
        results['mrr'].append(evaluator.mrr(retrieved_ids, truth))
    
    # 输出平均结果
    print("评估结果：")
    for metric, values in results.items():
        print(f"{metric}: {np.mean(values):.4f}")
    
    return results
```

## 6. 缓存实现

```python
import hashlib
import json
from datetime import datetime, timedelta

class QueryCache:
    """
    RAG查询缓存
    """
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl  # 缓存有效期（秒）
    
    def _generate_key(self, query, k):
        """生成缓存键"""
        key_data = f"{query}_{k}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query, k):
        """获取缓存"""
        key = self._generate_key(query, k)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return result
            else:
                del self.cache[key]
        
        return None
    
    def set(self, query, k, result):
        """设置缓存"""
        key = self._generate_key(query, k)
        self.cache[key] = (result, datetime.now())
    
    def clear_expired(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            k for k, (_, ts) in self.cache.items()
            if now - ts > timedelta(seconds=self.ttl)
        ]
        for k in expired_keys:
            del self.cache[k]

# 带缓存的RAG
class CachedRAG(SimpleRAG):
    def __init__(self, *args, cache_ttl=3600, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = QueryCache(ttl=cache_ttl)
    
    def query(self, question, k=5):
        """带缓存的查询"""
        # 检查缓存
        cached_result = self.cache.get(question, k)
        if cached_result:
            print("使用缓存结果")
            return cached_result
        
        # 执行查询
        result = super().query(question, k)
        
        # 缓存结果
        self.cache.set(question, k, result)
        
        return result
```

## 7. 使用LangChain的RAG

```python
from langchain import OpenAI, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

def build_langchain_rag(documents_path, embedding_model='all-MiniLM-L6-v2'):
    """
    使用LangChain构建RAG系统
    """
    # 1. 加载文档
    loader = TextLoader(documents_path)
    documents = loader.load()
    
    # 2. 分块
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    # 3. 创建嵌入和向量存储
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # 4. 创建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # 5. 创建QA链
    llm = OpenAI(temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    return qa_chain

# 使用
# qa = build_langchain_rag("docs.txt")
# result = qa({"query": "什么是RAG？"})
# print(result['result'])
# print(result['source_documents'])
```

## 相关笔记

- [[RAG-技术概述]] - 基础概念
- [[RAG-核心原理]] - 工作原理
- [[RAG-数据预处理与索引]] - 索引构建
- [[RAG-实时检索与重排序]] - 检索实现
- [[RAG-上下文构建与生成]] - 生成实现
- [[RAG-高级优化策略]] - 优化技巧

## 参考资料

- [Sentence-Transformers文档](https://www.sbert.net/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [LangChain文档](https://python.langchain.com/)
- [原文：RAG技术深度解析](https://juejin.cn/post/7501543492502683700)