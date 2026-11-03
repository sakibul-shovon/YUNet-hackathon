import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MESSAGES_DIR = ROOT / "apps" / "web" / "messages"


def get_all_keys(d, prefix=""):
    keys = set()
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(get_all_keys(v, full_key))
        else:
            keys.add(full_key)
    return keys


def test_t49_bilingual_message_parity():
    """T49: Full parity between English and Bangla message catalogues."""
    with open(MESSAGES_DIR / "en.json", "r", encoding="utf-8") as f:
        en = json.load(f)
    with open(MESSAGES_DIR / "bn.json", "r", encoding="utf-8") as f:
        bn = json.load(f)

    en_keys = get_all_keys(en)
    bn_keys = get_all_keys(bn)

    # Parity check
    assert en_keys == bn_keys, f"i18n mismatch: en-bn diff={en_keys ^ bn_keys}"
    assert len(en_keys) >= 100, f"Expected comprehensive catalogue, got {len(en_keys)} keys"


def test_t49_english_default_configuration():
    """T49: Verify default locale is explicitly English."""
    i18n_config = ROOT / "apps" / "web" / "src" / "lib" / "i18n" / "config.ts"
    content = i18n_config.read_text(encoding="utf-8")
    assert "defaultLocale: Locale = 'en'" in content
    assert "'en', 'bn'" in content


def test_t50_theme_default_and_tokens():
    """T50: Verify light default and complete semantic CSS variables for dark baseline."""
    globals_css = ROOT / "apps" / "web" / "src" / "app" / "globals.css"
    content = globals_css.read_text(encoding="utf-8")

    # Light tokens present
    assert "--canvas:#f7f6f2;" in content
    assert "--surface:#fff;" in content
    assert "--brand:#b13f2c;" in content

    # Dark baseline tokens present
    assert ".dark" in content
    assert "--canvas:#151a1d;" in content
    assert "--surface:#1e2529;" in content
    assert "--brand:#f49278;" in content

    # Default html theme in layout
    layout_tsx = ROOT / "apps" / "web" / "src" / "app" / "[locale]" / "layout.tsx"
    layout_content = layout_tsx.read_text(encoding="utf-8")
    assert 'className="light"' in layout_content
