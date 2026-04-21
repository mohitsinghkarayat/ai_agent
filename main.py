import os
import uuid
from dotenv import load_dotenv
load_dotenv()
from agent import create_agent

# Use simple ANSI escapes for basic coloring
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'

def main():
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}Welcome to AutoStream's Inflx Agent Terminal{RESET}")
    print(f"{CYAN}Type 'quit' or 'exit' to stop.{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    # Check for API key
    if "GROQ_API_KEY" not in os.environ:
        print(f"{RED}ERROR: GROQ_API_KEY environment variable is not set.{RESET}")
        print("Please set your Groq API key in your terminal before running:")
        print("set GROQ_API_KEY=your_api_key  (Windows)")
        print("export GROQ_API_KEY=your_api_key (Mac/Linux)")
        return

    agent_app = create_agent()
    # Create a unique thread_id to persist state across this session
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input(f"\n{GREEN}You: {RESET}")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        print(f"{YELLOW}Agent is thinking...{RESET}")
        
        try:
            # Invoke the LangGraph agent
            response = agent_app.invoke(
                {"messages": [("user", user_input)]},
                config=config
            )
            
            # The response contains the updated state, we extract the last AI message
            messages = response.get("messages", [])
            if messages:
                last_message = messages[-1].content
                print(f"{BLUE}Inflx:\n{last_message}{RESET}")
        except Exception as e:
            print(f"{RED}An error occurred: {e}{RESET}")

if __name__ == "__main__":
    main()
