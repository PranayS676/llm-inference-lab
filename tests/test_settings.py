from __future__ import annotations

import pytest

from runpod_inference_lab.common.settings import Settings


def test_settings_omits_chat_template_kwargs_by_default(monkeypatch):
    monkeypatch.delenv("CHAT_TEMPLATE_ENABLE_THINKING", raising=False)

    settings = Settings.from_env()

    assert settings.chat_template_enable_thinking is None
    assert settings.default_extra_body is None


def test_settings_builds_qwen_thinking_extra_body(monkeypatch):
    monkeypatch.setenv("CHAT_TEMPLATE_ENABLE_THINKING", "false")

    settings = Settings.from_env()

    assert settings.chat_template_enable_thinking is False
    assert settings.default_extra_body == {
        "chat_template_kwargs": {
            "enable_thinking": False,
        }
    }


def test_settings_rejects_invalid_bool(monkeypatch):
    monkeypatch.setenv("CHAT_TEMPLATE_ENABLE_THINKING", "maybe")

    with pytest.raises(ValueError, match="CHAT_TEMPLATE_ENABLE_THINKING"):
        Settings.from_env()
