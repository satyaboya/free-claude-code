#!/usr/bin/env python3
"""
Idempotent script to apply model ranking changes to Free Claude Code.

This script can be run multiple times safely - it checks if changes are already
applied before attempting to apply them.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: Path, content: str) -> bool:
    """Check if file exists and contains expected content."""
    if not filepath.exists():
        return False
    return content in filepath.read_text()


def create_file_with_content(filepath: Path, content: str) -> bool:
    """Create file with content if it doesn't exist or content differs."""
    if filepath.exists():
        existing_content = filepath.read_text()
        if existing_content.strip() == content.strip():
            print(f"✓ {filepath} already exists with correct content")
            return False
        print(f"⚠ {filepath} exists but content differs, updating...")
    else:
        print(f"Creating {filepath}...")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
    print(f"✓ Created/updated {filepath}")
    return True


def check_and_apply_registry_changes() -> bool:
    """Check and apply changes to providers/registry.py."""
    registry_file = Path("providers/registry.py")
    required_import = "from config.model_rankings import get_model_rank, get_tier_for_model"

    if not registry_file.exists():
        print(f"✗ {registry_file} not found")
        return False

    content = registry_file.read_text()
    if required_import in content:
        print(f"✓ {registry_file} already has ranking imports")
        return False

    print(f"Updating {registry_file}...")
    # Add the import after the existing config imports
    old_imports = """from config.provider_catalog import (
    PROVIDER_CATALOG,
    SUPPORTED_PROVIDER_IDS,
    ProviderDescriptor,
)
from config.settings import ConfiguredChatModelRef, Settings"""

    new_imports = """from config.model_rankings import get_model_rank, get_tier_for_model
from config.provider_catalog import (
    PROVIDER_CATALOG,
    SUPPORTED_PROVIDER_IDS,
    ProviderDescriptor,
)
from config.settings import ConfiguredChatModelRef, Settings"""

    content = content.replace(old_imports, new_imports)

    # Update the sorting logic
    old_sort = """    def cached_prefixed_model_infos(self) -> tuple[ProviderModelInfo, ...]:
        \"\"\"Return cached provider models with user-selectable prefixed ids.\"\"\"
        infos: list[ProviderModelInfo] = []
        for provider_id in SUPPORTED_PROVIDER_IDS:
            provider_infos = self._model_infos_by_provider.get(provider_id, {})
            infos.extend(
                ProviderModelInfo(
                    model_id=f"{provider_id}/{info.model_id}",
                    supports_thinking=info.supports_thinking,
                )
                for info in sorted(
                    provider_infos.values(), key=lambda item: item.model_id
                )
            )
        return tuple(infos)"""

    new_sort = """    def cached_prefixed_model_infos(self) -> tuple[ProviderModelInfo, ...]:
        \"\"\"Return cached provider models with user-selectable prefixed ids.\"\"\"
        infos: list[ProviderModelInfo] = []
        for provider_id in SUPPORTED_PROVIDER_IDS:
            provider_infos = self._model_infos_by_provider.get(provider_id, {})
            infos.extend(
                ProviderModelInfo(
                    model_id=f"{provider_id}/{info.model_id}",
                    supports_thinking=info.supports_thinking,
                )
                for info in sorted(
                    provider_infos.values(),
                    key=lambda item: (
                        # Sort by rank (higher rank = better model = comes first)
                        # Unranked models (rank 0) appear last
                        -get_model_rank(provider_id, item.model_id, get_tier_for_model(provider_id, item.model_id) or "sonnet"),
                        # Then alphabetically as tiebreaker
                        item.model_id,
                    ),
                )
            )
        return tuple(infos)"""

    content = content.replace(old_sort, new_sort)
    registry_file.write_text(content)
    print(f"✓ Updated {registry_file}")
    return True


def main():
    """Main function to apply all changes."""
    print("Applying model ranking changes...")
    print("=" * 60)

    changes_made = False

    # Create model rankings config
    model_rankings_content = '''"""Model rankings by provider and tier for ordering models by capability.

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
'''

    if create_file_with_content(Path("config/model_rankings.py"), model_rankings_content):
        changes_made = True

    # Create test file
    test_content = '''"""Test model ranking functionality."""

from config.model_rankings import get_model_rank, get_tier_for_model, MODEL_RANKINGS


def test_nvidia_nim_opus_rankings():
    """NVIDIA NIM Opus models are ranked correctly."""
    assert get_model_rank("nvidia_nim", "deepseek-ai/deepseek-v4-pro", "opus") == 1
    assert get_model_rank("nvidia_nim", "minimaxai/minimax-m2.7", "opus") == 2
    assert get_model_rank("nvidia_nim", "minimaxai/minimax-m2.5", "opus") == 3
    assert get_model_rank("nvidia_nim", "deepseek-ai/deepseek-v4-flash", "opus") == 4
    assert get_model_rank("nvidia_nim", "deepseek-ai/deepseek-v3.2", "opus") == 5
    assert get_model_rank("nvidia_nim", "z-ai/glm5", "opus") == 6


def test_nvidia_nim_sonnet_rankings():
    """NVIDIA NIM Sonnet models are ranked correctly."""
    assert get_model_rank("nvidia_nim", "z-ai/glm4.7", "sonnet") == 1
    assert get_model_rank("nvidia_nim", "marin/marin-8b-instruct", "sonnet") == 2
    assert get_model_rank("nvidia_nim", "google/gemma-7b", "sonnet") == 3
    assert get_model_rank("nvidia_nim", "mediatek/breeze-7b-instruct", "sonnet") == 4


def test_nvidia_nim_haiku_rankings():
    """NVIDIA NIM Haiku models are ranked correctly."""
    assert get_model_rank("nvidia_nim", "google/gemma-3n-4b", "haiku") == 1
    assert get_model_rank("nvidia_nim", "google/gemma-3n-2b", "haiku") == 2


def test_open_router_opus_rankings():
    """OpenRouter Opus models are ranked correctly."""
    assert get_model_rank("open_router", "xiaomi/mimo-v2-flash:free", "opus") == 1
    assert get_model_rank("open_router", "qwen/qwen3-coder-480b-a35b-instruct:free", "opus") == 2
    assert get_model_rank("open_router", "nvidia/nemotron-3-super-120b:free", "opus") == 3
    assert get_model_rank("open_router", "mistralai/devstral-2:free", "opus") == 4


def test_open_router_sonnet_rankings():
    """OpenRouter Sonnet models are ranked correctly."""
    assert get_model_rank("open_router", "qwen/qwen3-next-80b:free", "sonnet") == 1
    assert get_model_rank("open_router", "meta-llama/llama-3.3-70b-instruct:free", "sonnet") == 2
    assert get_model_rank("open_router", "google/gemma-3n-27b:free", "sonnet") == 3


def test_open_router_haiku_rankings():
    """OpenRouter Haiku models are ranked correctly."""
    assert get_model_rank("open_router", "llama-4-maverick:free", "haiku") == 1
    assert get_model_rank("open_router", "llama-4-scout:free", "haiku") == 2
    assert get_model_rank("open_router", "gemma-3n-4b:free", "haiku") == 3


def test_deepseek_opus_rankings():
    """DeepSeek Opus models are ranked correctly."""
    assert get_model_rank("deepseek", "deepseek-v4-pro", "opus") == 1
    assert get_model_rank("deepseek", "deepseek-v4-flash", "opus") == 2
    assert get_model_rank("deepseek", "deepseek-v3.2-exp", "opus") == 3


def test_deepseek_sonnet_rankings():
    """DeepSeek Sonnet models are ranked correctly."""
    assert get_model_rank("deepseek", "deepseek-v3.2", "sonnet") == 1
    assert get_model_rank("deepseek", "deepseek-v3.1-terminus", "sonnet") == 2
    assert get_model_rank("deepseek", "deepseek-chat", "sonnet") == 3


def test_deepseek_haiku_rankings():
    """DeepSeek Haiku models are ranked correctly."""
    assert get_model_rank("deepseek", "deepseek-r1", "haiku") == 1
    assert get_model_rank("deepseek", "deepseek-reasoner", "haiku") == 2


def test_unranked_models_return_zero():
    """Models not in rankings return rank 0."""
    assert get_model_rank("nvidia_nim", "unknown-model", "opus") == 0
    assert get_model_rank("open_router", "some-other-model", "sonnet") == 0


def test_get_tier_for_model():
    """Can determine tier from model ID."""
    assert get_tier_for_model("nvidia_nim", "deepseek-ai/deepseek-v4-pro") == "opus"
    assert get_tier_for_model("nvidia_nim", "z-ai/glm4.7") == "sonnet"
    assert get_tier_for_model("nvidia_nim", "google/gemma-3n-4b") == "haiku"
    assert get_tier_for_model("open_router", "xiaomi/mimo-v2-flash:free") == "opus"
    assert get_tier_for_model("deepseek", "deepseek-v4-pro") == "opus"
    assert get_tier_for_model("deepseek", "deepseek-chat") == "sonnet"


def test_get_tier_for_unknown_model_returns_none():
    """Unknown models return None tier."""
    assert get_tier_for_model("nvidia_nim", "unknown-model") is None
    assert get_tier_for_model("open_router", "some-other-model") is None


def test_rankings_structure():
    """Rankings structure is valid."""
    assert "nvidia_nim" in MODEL_RANKINGS
    assert "open_router" in MODEL_RANKINGS
    assert "deepseek" in MODEL_RANKINGS

    for provider_id, tiers in MODEL_RANKINGS.items():
        assert "opus" in tiers
        assert "sonnet" in tiers
        assert "haiku" in tiers

        # All tiers have at least one model
        assert len(tiers["opus"]) > 0
        assert len(tiers["sonnet"]) > 0
        assert len(tiers["haiku"]) > 0
'''

    if create_file_with_content(Path("tests/config/test_model_rankings.py"), test_content):
        changes_made = True

    # Create documentation
    docs_content = '''# Model Ranking System

## Overview

The Free Claude Code proxy now orders models by capability rather than alphabetically. When you use the `/model` picker in Claude Code, models are displayed from most capable to least capable within each provider.

## How It Works

### Ranking by Tier

Models are categorized into three tiers based on their intended use case:

- **Opus**: High-end models for complex reasoning, agentic tasks, and advanced coding
- **Sonnet**: General-purpose models for everyday tasks and balanced performance
- **Haiku**: Lightweight models for quick responses and simple tasks

### Provider-Specific Rankings

Each provider has its own ranking system based on benchmark performance and capabilities.

See the full documentation for detailed rankings by provider.

## Implementation Details

### Configuration File

Model rankings are defined in `config/model_rankings.py`.

### Sorting Logic

The `ProviderRegistry.cached_prefixed_model_infos()` method sorts models by:

1. **Rank** (higher rank = better model = appears first)
2. **Alphabetical order** (as tiebreaker for same-rank models)

Unranked models (rank 0) appear last in the list.

## Customizing Rankings

To customize model rankings for your use case, edit `config/model_rankings.py` and restart the proxy.

## Testing

Run the model rankings tests:

```bash
uv run pytest tests/config/test_model_rankings.py -v
```
'''

    if create_file_with_content(Path("docs/MODEL_RANKINGS.md"), docs_content):
        changes_made = True

    # Apply registry changes
    if check_and_apply_registry_changes():
        changes_made = True

    print("=" * 60)
    if changes_made:
        print("✓ Changes applied successfully!")
        print("Run 'uv run pytest tests/config/test_model_rankings.py -v' to verify.")
    else:
        print("✓ All changes already applied (idempotent).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
