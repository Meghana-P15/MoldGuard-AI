from __future__ import annotations

import json
from strands import Agent, tool

from agentic.prompts import KNOWLEDGE_PROMPT
from agentic.knowledge import get_knowledge_index


@tool
def search_process_knowledge(query: str, k: int = 3) -> str:
    """Retrieve relevant machine SOP, material or process guidance."""
    return json.dumps(get_knowledge_index().search(query, k=max(1, min(k, 5))))


def build_knowledge_agent(model=None) -> Agent:
    kwargs = {
        "name": "process_knowledge_specialist",
        "system_prompt": KNOWLEDGE_PROMPT,
        "tools": [search_process_knowledge],
    }
    if model is not None:
        kwargs["model"] = model
    return Agent(**kwargs)
