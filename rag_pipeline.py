import json
import os
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import create_retriever_tool

def get_retriever():
    """Builds a simple local RAG retriever from kb.json"""
    # Load knowledge base
    file_path = os.path.join(os.path.dirname(__file__), "data", "kb.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert JSON to text chunks (Documents)
    documents = []
    
    # Chunk 1: Company Info
    doc_company = Document(
        page_content=f"{data['company']}: {data['description']}",
        metadata={"source": "company_info"}
    )
    documents.append(doc_company)
    
    # Chunk 2: Basic Plan
    basic = data['plans']['Basic_Plan']
    doc_basic = Document(
        page_content=f"AutoStream Basic Plan: Costs {basic['price']}. Features include: {', '.join(basic['features'])}",
        metadata={"source": "pricing"}
    )
    documents.append(doc_basic)

    # Chunk 3: Pro Plan
    pro = data['plans']['Pro_Plan']
    doc_pro = Document(
        page_content=f"AutoStream Pro Plan: Costs {pro['price']}. Features include: {', '.join(pro['features'])}",
        metadata={"source": "pricing"}
    )
    documents.append(doc_pro)
    
    # Chunk 4: Policies
    doc_policies = Document(
        page_content=f"Company Policies. Refund Policy: {data['policies']['refund_policy']} Support Policy: {data['policies']['support']}",
        metadata={"source": "policies"}
    )
    documents.append(doc_policies)

    # We use local embeddings (HuggingFace) instead of Google since we're using Groq API
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = InMemoryVectorStore.from_documents(
        documents=documents,
        embedding=embeddings
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def setup_rag_tool():
    retriever = get_retriever()
    tool = create_retriever_tool(
        retriever,
        "search_autostream_knowledge_base",
        "Searches and returns information about AutoStream's pricing, plans, and company policies. Always use this to answer product questions."
    )
    return tool
