"""Test model ranking functionality."""

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
