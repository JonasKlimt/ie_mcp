"""
Builds the server instructions (the text an AI client reads when it connects) from
instructions.yaml: when to use the server, the trigger map and the routing rules.
"""

from __future__ import annotations

from typing import Any

from .config import INSTRUCTIONS_FILE, load_yaml


def trigger_groups() -> list[dict[str, Any]]:
    """Return the trigger groups of the instructions file.

    Returns:
        Dicts with name, triggers and check_first.
    """
    return load_yaml(INSTRUCTIONS_FILE)["trigger_groups"]


def render_trigger_map(heading: str, groups: list[dict[str, Any]]) -> str:
    """Write the trigger groups as one compact line each.

    Args:
        heading: Line above the list.
        groups: Trigger groups with name, triggers and check_first.

    Returns:
        The text block.
    """
    lines = [
        f"- {group['name']}: {', '.join(group['triggers'])} -> {', '.join(group['check_first'])}"
        for group in groups
    ]
    return "\n".join([heading, *lines])


def build_instructions() -> str:
    """Put the parts of instructions.yaml together in reading order.

    Returns:
        The complete instruction text for the MCP server.
    """
    document = load_yaml(INSTRUCTIONS_FILE)
    trigger_map = render_trigger_map(document["trigger_heading"], document["trigger_groups"])
    parts = [
        document["intro"],
        document["when_to_use"],
        trigger_map,
        document["fallback_rules"],
        document["routing_rules"],
        document["results_and_errors"],
        document["closing"],
    ]
    return "\n".join(part.strip() + "\n" for part in parts)
