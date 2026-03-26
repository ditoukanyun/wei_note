---
title: RAG上下文构建与生成
date: 2025-02-10
tags: [RAG, 上下文构建, LLM生成, 提示工程, Prompt, 文本生成]
category: 领域
status: active
parent: "[[MOC-RAG]]"
aliases: [RAG生成, 提示构建, Prompt Engineering]
---

# RAG上下文构建与生成

> **父级**：[[MOC-RAG]]  
> **上级**：[[RAG-核心原理]]  
> **相关**：[[RAG-实时检索与重排序]], [[RAG-代码示例]]

## 阶段概述

上下文构建与生成是RAG系统的**最终输出阶段**，将检索结果组织为提示词，调用LLM生成回答。

> [!info] 核心目标
> 将检索到的文档片段有效组织，引导LLM生成准确、连贯、有据可查的回答。

```mermaid
graph LR
    A[检索结果] --> B[文档组织]
    B --> C[提示构建]
    C --> D[LLM调用]
    D --> E[后处理]
    E --> F[最终输出]
```

## 1. 文档组织

### 上下文格式化

将检索到的文档片段整理为LLM可理解的格式：

```python
def format_context(documents, include_metadata=True):
    """
    格式化检索文档为上下文
    
    Args:
        documents: 检索到的文档列表
        include_metadata: 是否包含元数据
    
    Returns:
        格式化后的上下文字符串
    """
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        part = f"[文档{i}]\n{doc['content']}\n"
        
        if include_metadata and 'metadata' in doc:
            meta = doc['metadata']
            part += f"来源: {meta.get('source', '未知')}\n"
            part += f"页码: {meta.get('page', 'N/A')}\n"
        
        context_parts.append(part)
    
    return "\n---\n".join(context_parts)
```

### 上下文长度控制

```python
def truncate_context(context, max_tokens=3000):
    """截断上下文以适应模型限制"""
    # 简单字符估算（1 token ≈ 4字符）
    max_chars = max_tokens * 4
    
    if len(context) > max_chars:
        context = context[:max_chars] + "\n... [内容已截断]"
    
    return context
```

## 2. 提示工程（Prompt Engineering）

### 基础提示模板

```python
BASIC_PROMPT_TEMPLATE = """基于以下参考信息回答问题。

参考信息：
{context}

问题：{query}

请根据参考信息提供准确、简洁的回答。如果参考信息不足以回答问题，请明确说明。

回答："""
```

### 高级提示模板

```python
ADVANCED_PROMPT_TEMPLATE = """你是一个专业的问答助手。请基于提供的参考信息回答用户问题。

## 参考信息
{context}

## 回答要求
1. 仅基于上述参考信息回答，不要添加外部知识
2. 回答要准确、全面、简洁
3. 如果信息不足，请明确说明"根据提供的信息无法回答"
4. 如涉及数据，请确保准确性

## 用户问题
{query}

## 你的回答
"""
```

### 引用标注提示

```python
CITATION_PROMPT_TEMPLATE = """基于以下参考信息回答问题，并在回答中标注信息来源。

参考信息：
{context}

回答格式要求：
- 使用[1]、[2]等标注引用来源
- 在回答末尾列出引用文档
- 确保引用准确对应

问题：{query}

回答："""
```

## 3. LLM调用

### OpenAI API调用

```python
import openai

def generate_with_openai(prompt, model="gpt-3.5-turbo"):
    """使用OpenAI API生成回答"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的问答助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content
```

### 本地模型调用（Transformers）

```python
from transformers import pipeline

def generate_with_local(prompt, model_path="gpt2"):
    """使用本地模型生成回答"""
    generator = pipeline(
        "text-generation",
        model=model_path,
        device=0  # GPU
    )
    
    response = generator(
        prompt,
        max_length=500,
        temperature=0.7,
        do_sample=True,
        return_full_text=False
    )
    
    return response[0]['generated_text']
```

### LangChain集成

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def generate_with_langchain(query, context):
    """使用LangChain生成回答"""
    # 构建提示
    template = """基于以下上下文回答问题：
    
    上下文：
    {context}
    
    问题：{question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # 初始化模型
    model = ChatOpenAI(temperature=0.7)
    
    # 生成
    chain = prompt | model
    response = chain.invoke({
        "context": context,
        "question": query
    })
    
    return response.content
```

## 4. 完整RAG生成流程

```python
class RAGGenerator:
    def __init__(self, encoder, index, documents, llm_client):
        self.encoder = encoder
        self.index = index
        self.documents = documents
        self.llm = llm_client
    
    def retrieve(self, query, k=5):
        """检索相关文档"""
        query_emb = self.encoder.encode([query])
        _, indices = self.index.search(query_emb, k)
        return [self.documents[i] for i in indices[0]]
    
    def build_prompt(self, query, documents):
        """构建提示词"""
        context = self.format_context(documents)
        
        prompt = f"""基于以下信息回答问题：

{context}

问题：{query}
答案："""
        
        return prompt
    
    def generate(self, query):
        """完整的RAG生成流程"""
        # 1. 检索
        docs = self.retrieve(query)
        
        # 2. 构建提示
        prompt = self.build_prompt(query, docs)
        
        # 3. 生成回答
        answer = self.llm.generate(prompt)
        
        # 4. 返回结果和引用
        return {
            'answer': answer,
            'sources': docs,
            'prompt': prompt
        }
```

## 5. 生成优化策略

### 上下文压缩

```python
def compress_context(documents, query, encoder, max_length=2000):
    """
    基于查询相关性压缩上下文
    
    策略：只保留与查询最相关的句子或段落
    """
    query_emb = encoder.encode([query])[0]
    
    compressed = []
    current_length = 0
    
    for doc in documents:
        sentences = doc.split('。')
        
        for sent in sentences:
            if current_length + len(sent) > max_length:
                break
            
            # 计算句子与查询的相关性
            sent_emb = encoder.encode([sent])[0]
            similarity = cosine_similarity(query_emb, sent_emb)
            
            if similarity > 0.5:  # 阈值
                compressed.append(sent)
                current_length += len(sent)
    
    return '。'.join(compressed)
```

### 多文档融合

```python
def merge_documents(documents):
    """
    合并重叠的文档内容，去除冗余
    """
    seen_content = set()
    merged = []
    
    for doc in documents:
        # 提取关键句子
        key_sentences = extract_key_sentences(doc)
        
        for sent in key_sentences:
            if sent not in seen_content:
                merged.append(sent)
                seen_content.add(sent)
    
    return ' '.join(merged)
```

## 6. 后处理与引用

### 引用标注

```python
def add_citations(answer, documents):
    """
    在回答中添加引用标注
    """
    cited_answer = answer
    citations = []
    
    for i, doc in enumerate(documents, 1):
        # 简化示例：假设回答中提到了文档内容
        if doc['content'][:50] in answer:
            cited_answer = cited_answer.replace(
                doc['content'][:50],
                f"{doc['content'][:50]}[{i}]"
            )
            citations.append(f"[{i}] {doc['metadata']['source']}")
    
    return cited_answer + "\n\n参考来源：\n" + "\n".join(citations)
```

### 输出格式化

```python
def format_output(answer, sources, include_confidence=False):
    """格式化最终输出"""
    output = {
        'answer': answer,
        'sources': [
            {
                'content': s['content'][:200] + '...',
                'source': s['metadata']['source'],
                'page': s['metadata'].get('page')
            }
            for s in sources
        ]
    }
    
    if include_confidence:
        output['confidence'] = calculate_confidence(answer, sources)
    
    return output
```

## 7. 质量评估

### 自动评估指标

```python
def evaluate_answer(answer, sources, query):
    """
    评估回答质量
    """
    metrics = {}
    
    # 1. 忠实度（Faithfulness）
    # 检查回答是否忠实于来源文档
    metrics['faithfulness'] = check_faithfulness(answer, sources)
    
    # 2. 相关性（Relevance）
    # 检查回答是否相关于查询
    metrics['relevance'] = check_relevance(answer, query)
    
    # 3. 覆盖率（Coverage）
    # 检查是否涵盖了查询的关键点
    metrics['coverage'] = check_coverage(answer, query)
    
    return metrics
```

## 常见问题

> [!question] Q: 如何处理上下文过长？
> A: 1) 压缩上下文只保留关键信息 2) 使用支持长上下文的模型 3) 分块生成后汇总

> [!question] Q: 如何提高回答的准确性？
> A: 1) 优化检索质量 2) 在提示中强调只使用提供的信息 3) 添加校验步骤

> [!question] Q: 模型产生幻觉怎么办？
> A: 1) 在提示中明确约束 2) 使用引用标注强制基于文档 3) 后处理检查一致性

## 相关笔记

- [[RAG-核心原理]] - 整体架构
- [[RAG-实时检索与重排序]] - 上一阶段
- [[RAG-高级优化策略]] - 进阶优化
- [[RAG-代码示例]] - 完整代码实现

## 参考资料

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [原文：RAG技术深度解析](https://juejin.cn/post/7501543492502683700)