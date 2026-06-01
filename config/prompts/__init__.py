"""Prompt loader utility."""

from pathlib import Path

import yaml

from config.settings import PROMPTS_DIR


def get_prompt(name: str, **kwargs) -> str:
    """Load and format a prompt by name from the prompts YAML file."""
    prompts_path = PROMPTS_DIR / "stockgenie.yaml"
    if not prompts_path.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_path}")

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for p in data.get("prompts", []):
        if p["name"] == name:
            return p["prompt"].format(**kwargs)
    raise ValueError(f"Prompt '{name}' not found.")
