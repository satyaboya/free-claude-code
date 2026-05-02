"""Model rankings by provider and tier for ordering models by capability.

Models are ranked from most capable (rank 1) to least capable. Higher ranks indicate
better performance on coding, reasoning, and agentic tasks.
"""

from __future__ import annotations

from typing import Literal

Tier = Literal["opus", "sonnet", "haiku"]

# Provider-specific model rankings by tier
# Format: {provider_id: {tier: [model_id, ...]}}
# Models are listed in order of capability (best first)
MODEL_RANKINGS: dict[str, dict[Tier, list[str]]] = {
    "nvidia_nim": {
        "opus": [
            "deepseek-ai/deepseek-v4-pro",  # 1.6T MoE, 81% SWE-Bench Verified
            "minimaxai/minimax-m2.7",  # PinchBench 86.2%, 47% KiloBench
            "minimaxai/minimax-m2.5",  # SWE-Bench 80.2%
            "deepseek-ai/deepseek-v4-flash",  # 284B MoE, approaches Pro on simple tasks
            "deepseek-ai/deepseek-v3.2",  # Previous frontier
            "z-ai/glm5",  # BenchLM 83, below MiniMax on coding
        ],
        "sonnet": [
            "z-ai/glm4.7",  # Strong general model, repo default
            "marin/marin-8b-instruct",  # Reasoning/math/science-optimized 8B
            "google/gemma-7b",
            "mediatek/breeze-7b-instruct",
        ],
        "haiku": [
            "google/gemma-3n-4b",  # 4B > 2B by capacity
            "google/gemma-3n-2b",
        ],
    },
    "open_router": {
        "opus": [
            "xiaomi/mimo-v2-flash:free",  # #1 open-source SWE-Bench
            "qwen/qwen3-coder-480b-a35b-instruct:free",  # 480B MoE, top coding
            "nvidia/nemotron-3-super-120b:free",  # 120B hybrid MoE
            "mistralai/devstral-2:free",  # 123B dense coding
        ],
        "sonnet": [
            "qwen/qwen3-next-80b:free",  # 80B MoE optimized for agents/RAG
            "meta-llama/llama-3.3-70b-instruct:free",  # GPT-4-class general
            "google/gemma-3n-27b:free",  # 27B multilingual/multimodal
        ],
        "haiku": [
            "llama-4-maverick:free",
            "llama-4-scout:free",
            "gemma-3n-4b:free",
        ],
    },
    "deepseek": {
        "opus": [
            "deepseek-v4-pro",  # Strongest reasoning + agentic
            "deepseek-v4-flash",  # Approaches Pro, 12× cheaper
            "deepseek-v3.2-exp",  # Previous frontier
        ],
        "sonnet": [
            "deepseek-v3.2",
            "deepseek-v3.1-terminus",
            "deepseek-chat",  # V3 stable
        ],
        "haiku": [
            "deepseek-r1",  # Stronger chain-of-thought
            "deepseek-reasoner",  # Lighter alias
        ],
    },
}


def get_model_rank(provider_id: str, model_id: str, tier: Tier) -> int:
    """Get the rank of a model within its provider and tier.

    Returns 0 if the model is not ranked (unranked models appear last).
    """
    provider_rankings = MODEL_RANKINGS.get(provider_id, {})
    tier_models = provider_rankings.get(tier, [])

    try:
        return tier_models.index(model_id) + 1  # 1-based rank
    except ValueError:
        return 0  # Unranked


def get_tier_for_model(provider_id: str, model_id: str) -> Tier | None:
    """Determine which tier a model belongs to based on rankings.

    Returns None if the model is not in any tier ranking.
    """
    provider_rankings = MODEL_RANKINGS.get(provider_id, {})

    for tier, models in provider_rankings.items():
        if model_id in models:
            return tier

    return None
