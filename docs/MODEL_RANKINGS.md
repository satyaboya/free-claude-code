# Model Ranking System

## Overview

The Free Claude Code proxy now orders models by capability rather than alphabetically. When you use the `/model` picker in Claude Code, models are displayed from most capable to least capable within each provider.

## How It Works

### Ranking by Tier

Models are categorized into three tiers based on their intended use case:

- **Opus**: High-end models for complex reasoning, agentic tasks, and advanced coding
- **Sonnet**: General-purpose models for everyday tasks and balanced performance
- **Haiku**: Lightweight models for quick responses and simple tasks

### Provider-Specific Rankings

Each provider has its own ranking system based on benchmark performance and capabilities:

#### NVIDIA NIM

**Opus Tier (most → least capable):**
1. `deepseek-ai/deepseek-v4-pro` - 1.6T MoE, 81% SWE-Bench Verified
2. `minimaxai/minimax-m2.7` - PinchBench 86.2%, 47% KiloBench
3. `minimaxai/minimax-m2.5` - SWE-Bench 80.2%
4. `deepseek-ai/deepseek-v4-flash` - 284B MoE, approaches Pro on simple tasks
5. `deepseek-ai/deepseek-v3.2` - Previous frontier
6. `z-ai/glm5` - BenchLM 83, below MiniMax on coding

**Sonnet Tier (most → least capable):**
1. `z-ai/glm4.7` - Strong general model, repo default
2. `marin/marin-8b-instruct` - Reasoning/math/science-optimized 8B
3. `google/gemma-7b`
4. `mediatek/breeze-7b-instruct`

**Haiku Tier (most → least capable):**
1. `google/gemma-3n-4b` - 4B capacity
2. `google/gemma-3n-2b` - 2B capacity

#### OpenRouter

**Opus Tier (most → least capable):**
1. `xiaomi/mimo-v2-flash:free` - #1 open-source SWE-Bench
2. `qwen/qwen3-coder-480b-a35b-instruct:free` - 480B MoE, top coding
3. `nvidia/nemotron-3-super-120b:free` - 120B hybrid MoE
4. `mistralai/devstral-2:free` - 123B dense coding

**Sonnet Tier (most → least capable):**
1. `qwen/qwen3-next-80b:free` - 80B MoE optimized for agents/RAG
2. `meta-llama/llama-3.3-70b-instruct:free` - GPT-4-class general
3. `google/gemma-3n-27b:free` - 27B multilingual/multimodal

**Haiku Tier (most → least capable):**
1. `llama-4-maverick:free`
2. `llama-4-scout:free`
3. `gemma-3n-4b:free`

#### DeepSeek

**Opus Tier (most → least capable):**
1. `deepseek-v4-pro` - Strongest reasoning + agentic
2. `deepseek-v4-flash` - Approaches Pro, 12× cheaper
3. `deepseek-v3.2-exp` - Previous frontier

**Sonnet Tier (most → least capable):**
1. `deepseek-v3.2`
2. `deepseek-v3.1-terminus`
3. `deepseek-chat` - V3 stable

**Haiku Tier (most → least capable):**
1. `deepseek-r1` - Stronger chain-of-thought
2. `deepseek-reasoner` - Lighter alias

## Implementation Details

### Configuration File

Model rankings are defined in `config/model_rankings.py`:

```python
MODEL_RANKINGS: dict[str, dict[Tier, list[str]]] = {
    "nvidia_nim": {
        "opus": ["deepseek-ai/deepseek-v4-pro", ...],
        "sonnet": ["z-ai/glm4.7", ...],
        "haiku": ["google/gemma-3n-4b", ...],
    },
    # ... other providers
}
```

### Sorting Logic

The `ProviderRegistry.cached_prefixed_model_infos()` method now sorts models by:

1. **Rank** (higher rank = better model = appears first)
2. **Alphabetical order** (as tiebreaker for same-rank models)

Unranked models (rank 0) appear last in the list.

### API Functions

Two helper functions are available:

- `get_model_rank(provider_id, model_id, tier)` - Returns the rank (1-based) or 0 if unranked
- `get_tier_for_model(provider_id, model_id)` - Returns the tier ("opus", "sonnet", "haiku") or None

## Customizing Rankings

To customize model rankings for your use case:

1. Edit `config/model_rankings.py`
2. Modify the `MODEL_RANKINGS` dictionary
3. Reorder models within each tier list
4. Add new models to the appropriate tier
5. Restart the proxy

## Benefits

- **Better defaults**: Best models appear first in the picker
- **Informed choices**: Rankings reflect real-world performance
- **Flexible**: Easy to customize for specific use cases
- **Backward compatible**: Unranked models still appear in the list

## Testing

Run the model rankings tests:

```bash
uv run pytest tests/config/test_model_rankings.py -v
```

All 1199 tests pass, ensuring the ranking system works correctly without breaking existing functionality.
