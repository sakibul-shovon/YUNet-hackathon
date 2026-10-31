import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "services" / "backend"))

from app.main import app  # noqa: E402

CONTRACTS_DIR = ROOT / "packages" / "contracts"
OPENAPI_FILE = CONTRACTS_DIR / "openapi.json"
TS_FILE = CONTRACTS_DIR / "src" / "generated.ts"


def export_openapi() -> dict:
    openapi_schema = app.openapi()
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OPENAPI_FILE, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported OpenAPI schema to {OPENAPI_FILE}")
    return openapi_schema


def generate_typescript(schema: dict):
    lines = [
        "/**",
        " * Auto-generated ClaimCraft BD TypeScript API contracts.",
        " * DO NOT EDIT MANUALLY. Generated via: python scripts/tasks.py contracts",
        " */",
        "",
        "export interface ApiLiveHealth {",
        "  status: string;",
        "  app: string;",
        "  environment: string;",
        "  version: string;",
        "}",
        "",
        "export interface ApiReadyHealth {",
        "  status: string;",
        "  app: string;",
        "  environment: string;",
        "  capabilities: {",
        "    ai_provider: string;",
        "    stt_provider: string;",
        "    storage_backend: string;",
        "  };",
        "}",
        "",
        "export interface ApiPing {",
        "  message: string;",
        "}",
        "",
        "export interface ErrorResponse {",
        "  error: {",
        "    code: string;",
        "    message: string;",
        "    correlation_id?: string;",
        "    details?: Record<string, unknown>;",
        "  };",
        "}",
        "",
    ]

    components = schema.get("components", {}).get("schemas", {})
    for name, s in components.items():
        props = s.get("properties", {})
        required = s.get("required", [])
        lines.append(f"export interface {name} {{")
        for prop_name, prop_def in props.items():
            is_req = prop_name in required
            opt = "" if is_req else "?"
            t_type = "unknown"
            p_type = prop_def.get("type")
            if p_type == "string":
                t_type = "string"
            elif p_type in ("integer", "number"):
                t_type = "number"
            elif p_type == "boolean":
                t_type = "boolean"
            elif p_type == "array":
                t_type = "unknown[]"
            elif p_type == "object":
                t_type = "Record<string, unknown>"
            lines.append(f"  {prop_name}{opt}: {t_type};")
        lines.append("}\n")

    TS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated TypeScript contracts at {TS_FILE}")


def main():
    schema = export_openapi()
    generate_typescript(schema)


if __name__ == "__main__":
    main()

