from typing import Annotated
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from rag_pipeline import setup_rag_tool

@tool
def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Use this tool to capture the details of a high-intent user.
    ONLY call this tool AFTER you have successfully collected the user's name, email, and creator platform.
    """
    print(f"\n>>> [LEAD CAPTURED SUCCESSFULLY]: Name: {name}, Email: {email}, Platform: {platform} <<<\n")
    return "Lead captured! You can now inform the user that their details have been recorded and your team will reach out."

def create_agent():
    # Setup tools
    rag_tool = setup_rag_tool()
    tools = [rag_tool, mock_lead_capture]
    
    # Initialize the LLM (Groq as requested by user)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    
    # Define the System Prompt
    system_prompt = """You are Inflx, an AI agent for AutoStream, a SaaS product with automated video editing tools for content creators.

Process the user's message by classifying their intent into one of three categories:
1. "Casual greeting"
2. "Product or pricing inquiry"
3. "High-intent lead"

Then, follow these instructions:
- Casual greeting: Respond politely and briefly.
- Product or pricing inquiry: You MUST use the `search_autostream_knowledge_base` tool to fetch accurate information. Do not hallucinate prices or features.
- High-intent lead: If the user indicates they want to try a plan, sign up, or proceed, you must collect their Name, Email, and Creator Platform. If any are missing, ask for them. Once you have ALL THREE, execute the `mock_lead_capture` tool. Do NOT execute it prematurely.

Format your response exactly like this:
[INTENT: <Insert Intent Here>]
<Your conversational response or tool call>
"""

    # Persistent memory for state management across 5-6 turns
    memory = MemorySaver()
    
    # Compile Graph
    app = create_react_agent(
        llm, 
        tools=tools, 
        prompt=system_prompt,
        checkpointer=memory
    )
    
    return app
