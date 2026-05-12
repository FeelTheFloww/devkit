from devkit.config import DEFAULTS


def test_defaults_have_expected_keys() -> None:
    assert "ai_tool" in DEFAULTS
    assert "default_repo" in DEFAULTS
    assert "theme" in DEFAULTS
    assert "show_spinner" in DEFAULTS
