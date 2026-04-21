# Social-to-Lead Agentic Workflow

This repository contains the Inflx, an AI-powered conversational agent for the fictional SaaS company AutoStream. The agent seamlessly classifies user intents, answers product queries using a local RAG pipeline, and triggers a mock tool to capture high-intent leads.

## 1. How to run the project locally

1. Ensure you have **Python 3.9+** installed.
2. Open your terminal or command prompt in the project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Groq API Key in your console environment.
   - For Windows (Command Prompt): `set GROQ_API_KEY=your_api_key_here`
   - For Windows (PowerShell): `$env:GROQ_API_KEY="your_api_key_here"`
   - For Mac/Linux: `export GROQ_API_KEY=your_api_key_here`
5. Run the application:
   ```bash
   python main.py
   ```
6. Chat with the agent naturally!

## 2. Architecture Explanation

The agent is built primarily using **LangGraph** to maintain robust state management across the conversation, along with **Groq API** (via `langchain-groq`) for extremely fast, capable generation using open-weights models like Llama 3.

**State Management**: 
We utilize LangGraph’s persistent memory (`MemorySaver`). Every conversation thread uses a unique `thread_id`, preserving conversation history. This natively satisfies the memory requirements across multiple turns so the LLM knows what properties (Name, Email, Platform) have already been collected without resetting context.

**Intent & Control Flow**:
We use LangGraph's prebuilt React wrapper combined with an explicitly configured system prompt. The prompt acts as a strict guardrail, forcing the LLM to execute reasoning before responding by declaring the user intent.

**RAG Retrieval**:
The RAG pipeline operates over a local JSON file (`data/kb.json`). The documents are loaded into LangChain’s `InMemoryVectorStore` using `HuggingFaceEmbeddings` (all-MiniLM-L6-v2) for free local embeddings without API constraints. This store exposes a retriever tool which the agent contextually invokes when it detects a "Product or pricing inquiry" intent.

**Tool Execution**:
The agent is provided with a `mock_lead_capture` tool. Following ReAct patterns, it only calls this tool when it assesses that the high-intent lead parameters (Name, Email, Platform) are successfully satisfied.

## 3. WhatsApp Deployment Question

**Q: Explain how you would integrate this agent with WhatsApp using Webhooks.**

To deploy this intelligent agent on WhatsApp, I would use the **WhatsApp Business Cloud API** combined with a fast webhook server like **FastAPI** or Flask.

1. **Webhook Endpoint**: Create a public URL endpoint (using `ngrok` for local testing) configured as the WhatsApp Webhook in the Meta Developer platform. Meta sends HTTP POST requests here when users interact.
2. **Event Parsing & State**: Extract the incoming text message and the sender's WhatsApp phone number from the JSON payload. The phone number serves excellently as the LangGraph `thread_id`, tying the user to a specific conversation state in the `MemorySaver`.
3. **Agent Invocation**: The webhook endpoint invokes the LangGraph agent (`agent_app.invoke()`) asynchronously with the user's message. The agent executes RAG tools, intent detection, and internal tool routing natively.
4. **Sending Responses**: Extract the final computed `.content` from the last message in LangGraph's updated state. We then immediately fire an HTTP POST request back to WhatsApp's API `/messages` endpoint bearing the AI-generated text to be delivered back to the user's phone.
