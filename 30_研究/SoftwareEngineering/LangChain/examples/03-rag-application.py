"""
LangChain 基础示例 3: RAG 应用
展示如何构建一个简单的文档问答系统
"""

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os


def create_sample_document():
    """创建示例文档"""
    sample_text = """
LangChain 是一个用于构建基于 LLM 应用程序的框架。

什么是 LangChain？
LangChain 是一个开源框架，旨在帮助开发者构建由大型语言模型（LLM）驱动的应用程序。
它提供了一套工具和抽象，使开发者能够轻松地将 LLM 与外部数据源、API 和其他工具集成。

核心组件：
1. Chains（链）：将多个组件组合成可复用的工作流
2. Agents（代理）：让 LLM 自主决定采取什么行动
3. Memory（记忆）：在多轮对话中保持上下文
4. Retrieval（检索）：与外部数据源集成，实现 RAG
5. Prompts（提示词）：管理和优化提示词模板

为什么使用 LangChain？
- 标准化接口：统一不同 LLM 提供商的 API
- 快速开发：用不到 10 行代码构建代理
- 灵活性：从简单到复杂的应用都能支持
- 生态系统：丰富的集成和扩展

LangChain vs LangGraph vs Deep Agents：
- Deep Agents：开箱即用，适合快速启动
- LangChain：平衡简单性和灵活性，推荐使用
- LangGraph：低级别编排，适合高级定制

应用场景：
- 文档问答系统
- 智能客服代理
- 代码助手
- 知识管理系统
- 自动化工作流

开始使用：
安装：pip install langchain
文档：https://docs.langchain.com/
GitHub：https://github.com/langchain-ai/langchain
"""
    
    with open("sample_doc.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    
    return "sample_doc.txt"


def build_rag_system(document_path: str):
    """
    构建 RAG 系统
    
    步骤：
    1. 加载文档
    2. 分割文本
    3. 创建向量存储
    4. 构建检索链
    """
    
    print("步骤 1: 加载文档...")
    loader = TextLoader(document_path, encoding="utf-8")
    documents = loader.load()
    print(f"  加载了 {len(documents)} 个文档")
    
    print("\n步骤 2: 分割文本...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,        # 每块大小
        chunk_overlap=50,      # 重叠大小
        separators=["\n\n", "\n", "。", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    print(f"  分割成 {len(texts)} 个文本块")
    
    print("\n步骤 3: 创建向量存储...")
    # 需要 OPENAI_API_KEY 环境变量
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)
    print("  向量存储创建完成")
    
    # 保存向量存储（可选）
    vectorstore.save_local("faiss_index")
    print("  向量索引已保存到 faiss_index/")
    
    print("\n步骤 4: 构建检索链...")
    
    # 自定义提示词模板
    prompt_template = """基于以下上下文回答问题。如果无法从上下文中找到答案，请说"根据提供的文档，我无法回答这个问题"。

上下文：
{context}

问题：{question}

请提供详细且准确的答案："""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # 创建检索链
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        chain_type="stuff",  # 将文档填入提示词
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 3}  # 检索最相关的3个文档
        ),
        return_source_documents=True,  # 返回引用的文档
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("  RAG 系统构建完成！")
    
    return qa_chain


def query_rag_system(qa_chain, question: str):
    """
    查询 RAG 系统
    
    Args:
        qa_chain: 检索链
        question: 用户问题
    
    Returns:
        答案和来源文档
    """
    print(f"\n问题: {question}")
    print("-" * 60)
    
    result = qa_chain({"query": question})
    
    print(f"\n答案:\n{result['result']}")
    
    print(f"\n来源文档 ({len(result['source_documents'])} 个):")
    for i, doc in enumerate(result['source_documents'], 1):
        print(f"\n[{i}] {doc.page_content[:150]}...")
    
    return result


def main():
    """主函数"""
    
    # 检查 API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        print("export OPENAI_API_KEY='your-api-key'")
        return
    
    print("=" * 60)
    print("LangChain RAG 应用示例")
    print("=" * 60)
    
    # 创建示例文档
    print("\n创建示例文档...")
    doc_path = create_sample_document()
    print(f"文档已创建: {doc_path}")
    
    # 构建 RAG 系统
    print("\n" + "=" * 60)
    print("构建 RAG 系统")
    print("=" * 60)
    
    try:
        qa_chain = build_rag_system(doc_path)
    except Exception as e:
        print(f"构建 RAG 系统失败: {e}")
        return
    
    # 测试查询
    print("\n" + "=" * 60)
    print("测试查询")
    print("=" * 60)
    
    test_questions = [
        "什么是 LangChain？",
        "LangChain 的核心组件有哪些？",
        "LangChain 和 LangGraph 有什么区别？",
        "如何安装 LangChain？",
        "LangChain 有哪些应用场景？",
        "Python 是谁创建的？"  # 这个问题文档中没有答案
    ]
    
    for question in test_questions:
        query_rag_system(qa_chain, question)
        input("\n按 Enter 继续...")
    
    # 交互模式
    print("\n" + "=" * 60)
    print("进入交互模式 (输入 'exit' 退出)")
    print("=" * 60)
    
    while True:
        user_input = input("\n你的问题: ").strip()
        if user_input.lower() == 'exit':
            print("再见！")
            break
        
        query_rag_system(qa_chain, user_input)
    
    # 清理
    if os.path.exists(doc_path):
        os.remove(doc_path)
        print(f"\n清理: 已删除 {doc_path}")


if __name__ == "__main__":
    main()
