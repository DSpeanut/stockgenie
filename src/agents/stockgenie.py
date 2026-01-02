import os
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import operator
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from tools.tools import inventory_search_tool, market_price_tool, news_search_tool, get_prompt
from config.config import ENV_PATH


load_dotenv(ENV_PATH,override=True)
api_key = os.getenv("OPENAI_API_KEY")

print(api_key)

model = ChatOpenAI(api_key=api_key, model="gpt-4o")
checkpointer = MemorySaver()

# Augment the LLM with tools
tools = [market_price_tool, inventory_search_tool, news_search_tool]


# AgentState
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# Agent class
class Agent:
    def __init__(self, model, tools, checkpointer, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}
    
    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        print(tool_calls)
        results = []
        for t in tool_calls:
            print(f"Calling tool: {t['name']}")
            tool_function = self.tools.get(t['name'])
            if tool_function:
                try:
                    if isinstance(t['args'], dict):
                        result = tool_function.invoke(t['args'])
                    else:
                        result = tool_function.invoke({'input': t['args']})
                    
                    # This line was indented wrong - should be here!
                    results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
                    
                except Exception as e:
                    print(f"Error executing tool {t['name']}: {str(e)}")
                    results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=f"Error: {str(e)}"))
            else:
                print(f'Tool {t["name"]} not found')
                results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=f"Tool {t['name']} not found"))
        
        return {'messages': results}

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(getattr(result, "tool_calls", [])) > 0

def extract_messages(result):
    msgs = []
    if isinstance(result, dict):
        for val in result.values():
            if isinstance(val, list):
                for item in val:
                    if hasattr(item, 'content') or hasattr(item, 'tool_calls'):
                        msgs.append(item)
                    elif isinstance(item, dict):
                        msgs.extend(extract_messages(item))
            elif isinstance(val, dict):
                msgs.extend(extract_messages(val))
    return msgs

# Initialize agent
agent_bot = Agent(
    model,
     [inventory_search_tool, market_price_tool, news_search_tool],
    checkpointer=checkpointer,
    system=get_prompt("STOCK_GENIE_SYSTEM_PROMPT")
)

def run_agent(user_input, thread_id="default"):
    """Run the agent with user input and return the response"""
    messages = [HumanMessage(content=user_input)]
    config = {"configurable": {"thread_id": thread_id}}
    
    result = agent_bot.graph.invoke({"messages": messages}, config)
    
    # Extract the final response
    if result and 'messages' in result:
        last_message = result['messages'][-1]
        if hasattr(last_message, 'content'):
            return last_message.content
    
    return "No response generated"

def main():
    """Main CLI function"""
    print("=" * 60)
    print("Stock Genie CLI")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'clear' to start a new conversation")
    print("-" * 60)
    
    thread_id = "new"
    
    # Check if input is provided as command line argument
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye!")
            return
        
        print(f"\nYou: {user_input}")
        print("\nAgent: ", end="", flush=True)
        response = run_agent(user_input, thread_id)
        print(response)
        return
    
    # Interactive mode
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            
            if user_input.lower() == 'clear':
                thread_id = f"cli_session_{os.urandom(1234).hex()}"
                print("\n[New conversation started]")
                continue
            
            print("\nAgent: ", end="", flush=True)
            response = run_agent(user_input, thread_id)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()
