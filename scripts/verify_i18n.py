import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MESSAGES_DIR = ROOT / "apps" / "web" / "messages"
EN_FILE = MESSAGES_DIR / "en.json"
BN_FILE = MESSAGES_DIR / "bn.json"


def get_keys(d, prefix=""):
    keys = set()
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(get_keys(v, full_key))
        else:
            keys.add(full_key)
    return keys


def main():
    if not EN_FILE.exists() or not BN_FILE.exists():
        print(f"Error: message files missing at {MESSAGES_DIR}", file=sys.stderr)
        sys.exit(1)

    with open(EN_FILE, "r", encoding="utf-8") as f:
        en_data = json.load(f)

    with open(BN_FILE, "r", encoding="utf-8") as f:
        bn_data = json.load(f)

    en_keys = get_keys(en_data)
    bn_keys = get_keys(bn_data)

    missing_in_bn = en_keys - bn_keys
    missing_in_en = bn_keys - en_keys

    ok = True
    if missing_in_bn:
        print(f"FAILED: {len(missing_in_bn)} keys missing in Bangla (bn.json):")
        for k in sorted(missing_in_bn):
            print(f"  - {k}")
        ok = False

    if missing_in_en:
        print(f"FAILED: {len(missing_in_en)} keys missing in English (en.json):")
        for k in sorted(missing_in_en):
            print(f"  - {k}")
        ok = False

    if ok:
        print(f"SUCCESS: Exact 1:1 i18n parity verified across {len(en_keys)} message keys!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

