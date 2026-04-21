from dotenv import load_dotenv
load_dotenv()
from agent import create_agent

app = create_agent()
config = {"configurable": {"thread_id": "test_123"}}

def test_chat(msg):
    print("="*40)
    print(f"USER: {msg}")
    res = app.invoke({"messages": [("user", msg)]}, config=config)
    print(f"\nAGENT:\n{res['messages'][-1].content}")
    print("="*40)

if __name__ == "__main__":
    test_chat("Hi, tell me about your pricing")
    test_chat("That sounds good, I want to try the Pro plan for my YouTube channel")
    test_chat("My name is John Doe")
    test_chat("My email is john@test.com")
