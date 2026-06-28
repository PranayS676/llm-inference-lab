from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_expected_scripts_exist():
    for relative in [
        "servers/start_vllm.sh",
        "servers/start_sglang.sh",
        "servers/health_check.sh",
        "servers/stop_servers.sh",
        "scripts/setup_runpod.sh",
        "scripts/run_a100_baseline.sh",
        "scripts/run_h200_long_context.sh",
    ]:
        assert (ROOT / relative).exists(), relative


def test_health_check_uses_authorization_header():
    text = (ROOT / "servers/health_check.sh").read_text(encoding="utf-8")

    assert "Authorization: Bearer" in text
