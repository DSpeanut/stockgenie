"""Routing classifier: picks a skill (or the general loop) for the current turn."""

from langchain_core.messages import AnyMessage, SystemMessage
from pydantic import BaseModel, Field

from core.skills import SkillSpec


class _RouteDecision(BaseModel):
    route: str = Field(description="The chosen route name.")


def route_question(model, messages: list[AnyMessage], skills: list[SkillSpec]) -> str:
    """Return a skill name from `skills`, or "general" if none clearly applies."""
    valid_routes = {s.name for s in skills} | {"general"}
    skill_lines = "\n".join(f"- {s.name}: {s.description}" for s in skills)
    system = (
        "You are a routing classifier for a financial advisor agent. Given the conversation, "
        "choose exactly one route by name.\n\n"
        f"Available skills:\n{skill_lines}\n\n"
        "- general: anything that doesn't clearly match a skill above — simple lookups, "
        "single-fact questions (a price, a currency rate, a news headline), or anything not "
        "covered by a skill's description.\n\n"
        "Choose a skill only when the request clearly matches its purpose. When in doubt, choose "
        "general."
    )
    structured_model = model.with_structured_output(_RouteDecision)
    decision = structured_model.invoke([SystemMessage(content=system)] + list(messages))
    return decision.route if decision.route in valid_routes else "general"
