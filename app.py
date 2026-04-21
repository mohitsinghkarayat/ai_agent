from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
from agent import create_agent

app = FastAPI(title="Inflx Agent Interface")

# Make sure static directory exists
if not os.path.exists(os.path.join(os.path.dirname(__file__), "static")):
    os.makedirs(os.path.join(os.path.dirname(__file__), "static"))

app.mount("/static", StaticFiles(directory="static"), name="static")

agent_app = create_agent()

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat(req: ChatRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    try:
        YELLOW = '\033[93m'
        BLUE = '\033[96m'
        RESET = '\033[0m'
        
        print(f"\n{YELLOW}========== NEW REQUEST =========={RESET}")
        print(f"{YELLOW}[USER] ->{RESET} {req.message}")
        
        # Invoke the LangGraph agent
        response = agent_app.invoke(
            {"messages": [("user", req.message)]},
            config=config
        )
        # Extract last message
        messages = response.get("messages", [])
        if messages:
            last_message = messages[-1].content
            print(f"{BLUE}[AGENT] ->{RESET} {last_message}")
            print(f"{YELLOW}================================={RESET}\n")
            return {"response": last_message}
        return {"response": "Error: Unrecognized response format from agent."}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
