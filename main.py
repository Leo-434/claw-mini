import asyncio
import os
import sys

# Ensure backend modules can be imported if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.graph.agent import stream_chat_response

async def run_cli():
    print("====================================")
    print("🤖 Welcome to ClawMini CLI 🤖")
    print("Type 'exit' or 'quit' to terminate.")
    print("====================================\n")
    
    session_id = "cli_session"
    
    while True:
        try:
            user_input = input("\n[User]: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if user_input.strip().lower() in ["exit", "quit", "q"]:
            break
            
        if not user_input.strip():
            continue
            
        print("[Agent]: ", end="", flush=True)
        
        # We need to iterate over the async generator
        async for chunk in stream_chat_response(user_input, session_id):
            # chunks are formatted as "data: {content}\n\n"
            content = chunk.replace("data: ", "").strip("\n")
            if content.startswith("[THOUGHT]"):
                # Print thoughts in a dimmed or distinct way
                print(f"\n   \033[90m{content}\033[0m")
            else:
                print(content, end="", flush=True)
                
        print() # newline after generation

def main():
    asyncio.run(run_cli())

if __name__ == "__main__":
    main()
