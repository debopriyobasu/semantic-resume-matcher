from pathlib import Path
from string import Formatter
from typing import Any

from src.core.config import get_settings


def load_prompt(prompt_name: str) -> str:
    prompt_path = _prompt_path(prompt_name)
    return prompt_path.read_text(encoding="utf-8")


def render_prompt(prompt_name: str, variables: dict[str, Any]) -> str:
    template = load_prompt(prompt_name)
    expected_variables = {
        field_name for _, field_name, _, _ in Formatter().parse(template) if field_name is not None
    }
    missing_variables = expected_variables - variables.keys()

    if missing_variables:
        missing = ", ".join(sorted(missing_variables))
        raise KeyError(f"Missing prompt variables: {missing}")

    return template.format(**variables)


def _prompt_path(prompt_name: str) -> Path:
    if Path(prompt_name).name != prompt_name:
        raise ValueError("Prompt name must be a file name, not a path")

    prompt_dir = Path(get_settings().prompt_dir)
    prompt_path = prompt_dir / prompt_name

    if prompt_path.suffix != ".md":
        raise ValueError("Prompt name must end with .md")

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_name}")

    return prompt_path
