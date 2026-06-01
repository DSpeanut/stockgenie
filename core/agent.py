"""Agent orchestration: LangGraph nodes and conditional edges."""

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END

from core.state import AgentState


class Agent:
    """Re-entrant agent that binds an LLM to a set of tools via a compiled graph."""

    def __init__(self, model, tools, checkpointer, system: str = ""):
        from langgraph.graph import StateGraph

        self.system = system
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)

    def call_openai(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {"messages": [message]}

    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            tool_function = self.tools.get(t["name"])
            if tool_function:
                try:
                    if isinstance(t["args"], dict):
                        result = tool_function.invoke(t["args"])
                    else:
                        result = tool_function.invoke({"input": t["args"]})
                    results.append(
                        ToolMessage(
                            tool_call_id=t["id"], name=t["name"], content=str(result)
                        )
                    )
                except Exception as e:
                    results.append(
                        ToolMessage(
                            tool_call_id=t["id"],
                            name=t["name"],
                            content=f"Error: {e!s}",
                        )
                    )
            else:
                results.append(
                    ToolMessage(
                        tool_call_id=t["id"],
                        name=t["name"],
                        content=f"Tool {t['name']} not found",
                    )
                )
        return {"messages": results}

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(getattr(result, "tool_calls", [])) > 0


def run_agent(user_input: str, thread_id: str = "default") -> str:
    """Run the agent with user input and return the final response string."""
    from core.graph import build_agent

    agent = build_agent()
    messages = [HumanMessage(content=user_input)]
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.graph.invoke({"messages": messages}, config)

    if result and "messages" in result:
        last_message = result["messages"][-1]
        if hasattr(last_message, "content"):
            return str(last_message.content)
    return "No response generated"
