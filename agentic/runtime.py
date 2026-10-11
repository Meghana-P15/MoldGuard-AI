from __future__ import annotations

from functools import lru_cache

from ai.moldguard_ai.runtime import ModelBundle
from agentic.artifacts import ensure_model_artifacts


@lru_cache(maxsize=1)
def get_bundle() -> ModelBundle:
    return ModelBundle.load(ensure_model_artifacts())
