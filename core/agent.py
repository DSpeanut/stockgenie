"""Agent orchestration: LangGraph nodes and conditional edges."""

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END

from core.router import route_question
from core.skills import SkillSpec
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
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
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
                    results.append(ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result)))
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


class Orchestrator:
    """Top-level graph: routes each turn to either the general loop or a scoped skill loop.

    Both branches run the same `llm <-> action` loop shape (via `Agent`), just bound to
    different instructions and a different tool list. `general_exec` and `skill_exec` invoke
    their agent's compiled graph imperatively rather than nesting it as a LangGraph subgraph,
    so each branch gets its own independent recursion budget that never counts against the
    outer graph's.
    """

    GENERAL_RECURSION_LIMIT = 15
    SKILL_RECURSION_LIMIT = 20

    def __init__(self, model, general_agent: Agent, skills: list[SkillSpec], checkpointer):
        from langgraph.graph import StateGraph

        self.model = model
        self.general_agent = general_agent
        self.skills_by_name = {s.name: s for s in skills}
        self._skill_agents: dict[str, Agent] = {}

        graph = StateGraph(AgentState)
        graph.add_node("router", self._route)
        graph.add_node("general_exec", self._run_general)
        graph.add_node("skill_exec", self._run_skill)
        graph.add_conditional_edges(
            "router",
            lambda state: state["route"],
            {"general": "general_exec", **{name: "skill_exec" for name in self.skills_by_name}},
        )
        graph.add_edge("general_exec", END)
        graph.add_edge("skill_exec", END)
        graph.set_entry_point("router")
        self.graph = graph.compile(checkpointer=checkpointer)

    def _route(self, state: AgentState):
        route = route_question(self.model, state["messages"], list(self.skills_by_name.values()))
        return {"route": route}

    def _run_general(self, state: AgentState):
        result = self.general_agent.graph.invoke(
            {"messages": state["messages"]},
            {"recursion_limit": self.GENERAL_RECURSION_LIMIT},
        )
        return {"messages": [result["messages"][-1]]}

    def _run_skill(self, state: AgentState):
        skill = self.skills_by_name[state["route"]]
        agent = self._get_skill_agent(skill)
        result = agent.graph.invoke(
            {"messages": state["messages"]},
            {"recursion_limit": self.SKILL_RECURSION_LIMIT},
        )
        return {"messages": [result["messages"][-1]]}

    def _get_skill_agent(self, skill: SkillSpec) -> Agent:
        if skill.name not in self._skill_agents:
            self._skill_agents[skill.name] = Agent(
                model=self.model, tools=skill.tools, checkpointer=None, system=skill.instructions
            )
        return self._skill_agents[skill.name]


_agent: Orchestrator | None = None


def get_agent() -> Orchestrator:
    """Return a process-wide singleton orchestrator so conversation memory persists across requests."""
    global _agent
    if _agent is None:
        from core.graph import build_agent

        _agent = build_agent()
    return _agent


def run_agent(user_input: str, thread_id: str = "default") -> str:
    agent = get_agent()
    # Server-side formatting: request Markdown-structured output with explicit line breaks
    formatting_hint = (
        "FORMAT YOUR ANSWER USING MARKDOWN WITH THESE RULES:\n"
        "- Put EVERY heading (##, ###) on its OWN LINE.\n"
        "- Put a BLANK LINE between every paragraph and section.\n"
        "- Use bullet lists (- item) for key points — one bullet per line.\n"
        "- Use markdown tables (| col1 | col2 |) for numeric data.\n"
        "- Use **bold** for emphasis, not inline symbols.\n"
        "- Use --- (horizontal rule) on its OWN LINE between major sections.\n"
        "- Break long text into multiple short paragraphs — NEVER output a single long paragraph.\n"
    )
    messages = [HumanMessage(content=formatting_hint + "\n\n" + user_input)]
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 10,
    }
    result = agent.graph.invoke({"messages": messages}, config)

    if result and "messages" in result:
        last_message = result["messages"][-1]
        if hasattr(last_message, "content"):
            return clean_markdown(str(last_message.content))
    return "No response generated"


def clean_markdown(text: str) -> str:
    """Post-process LLM output to fix common markdown formatting errors."""
    import re

    lines = text.split("\n")
    out = []

    def is_row(line):
        return line.strip().startswith("|") and line.strip().endswith("|")

    def is_sep(line):
        stripped = line.strip()
        if not is_row(line):
            return False
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        return len(cells) > 0 and all(re.fullmatch(r"[\s\-:]+", c) for c in cells)

    i = 0
    while i < len(lines):
        # Detect a table: consecutive pipe-delimited rows
        if is_row(lines[i]):
            table_lines = []
            while i < len(lines) and is_row(lines[i]):
                table_lines.append(lines[i])
                i += 1

            # Strip all separator rows, keep header + data rows
            header = None
            data_rows = []
            for tl in table_lines:
                if is_sep(tl):
                    continue
                if header is None:
                    header = tl
                else:
                    data_rows.append(tl)

            if header and data_rows:
                out.append(header)
                cols = header.count("|") - 1
                out.append("|" + "|".join(["---"] * cols) + "|")
                out.extend(data_rows)
            elif header:
                out.append(header)
        else:
            out.append(lines[i])
            i += 1

    text = "\n".join(out)
    text = re.sub(r"([^\n])\n(#{1,6}\s)", r"\1\n\n\2", text)
    text = re.sub(r"([^\n])\n(>)", r"\1\n\n\2", text)
    return text


if __name__ == "__main__":
    import os
    import sys

    print("=" * 60)
    print("Stock Genie CLI")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'clear' to start a new conversation")
    print("-" * 60)

    thread_id = "cli"

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            sys.exit(0)
        print(f"\nYou: {user_input}")
        print("\nAgent: ", end="", flush=True)
        response = run_agent(user_input, thread_id)
        print(response)
        sys.exit(0)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break
            if user_input.lower() == "clear":
                import uuid

                thread_id = f"cli_{uuid.uuid4().hex[:8]}"
                print("\n[New conversation started]")
                continue
            print("\nAgent: ", end="", flush=True)
            response = run_agent(user_input, thread_id)
            print(response)
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e!s}")
            print("Please try again.")
