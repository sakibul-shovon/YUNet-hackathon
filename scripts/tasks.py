#!/usr/bin/env python3
"""
ClaimCraft BD — Cross-platform task runner and verification script.
Refer to plan.md Section 8.2 for standard command contracts.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT_DIR / ".agent" / "state.json"
DOCS_DIR = ROOT_DIR / "docs"

EXPECTED_SOURCE_HASHES = {
    "ClaimCraft_BD_Master_Product_Blueprint_v4.1_Knowledge_AI_Engineering.md": "6C4D97EE7988CFE35C90E6D2397CBA1D2E7B4AC47D2DF9C9253594C5C448E61A",
    "hacakthon details.txt": "65D607450DF631BEFAD35CF4D5A8A41DFA0ADF7A462AA46A7F32A4DA3608457B",
    "plan.md": "E998906D971726FC2656B0090EB398424F741B0844F4AD75DA345EECD6372636",
}


def is_windows() -> bool:
    return sys.platform.startswith("win")


def get_pnpm_cmd() -> str:
    return "pnpm.cmd" if is_windows() else "pnpm"


def compute_sha256(filepath: Path) -> str:
    raw = filepath.read_bytes()
    h_raw = hashlib.sha256(raw).hexdigest().upper()
    h_lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest().upper()
    expected = EXPECTED_SOURCE_HASHES.get(filepath.name)
    if expected and h_lf == expected:
        return h_lf
    return h_raw


def load_state():
    if not STATE_FILE.exists():
        print(f"Error: State file not found at {STATE_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def cmd_status(args):
    state = load_state()
    tasks = state.get("tasks", {})
    phases = state.get("phases", {})

    print("==================================================")
    print(" ClaimCraft BD — Task Ledger & Status")
    print("==================================================")
    print(f"Plan Version: {state.get('plan_version', 'Unknown')}")
    print(f"Current Task: {state.get('current_task', 'None')}")
    print(f"Last Completed: {state.get('last_completed_task', 'None')}")
    print(f"Mode: {state.get('environment', {}).get('mode', 'unconfigured')}")

    # Verify source document hashes
    print("\n--- Source Document Integrity ---")
    hash_ok = True
    for fname, expected_hash in EXPECTED_SOURCE_HASHES.items():
        fpath = (ROOT_DIR if fname == "plan.md" else DOCS_DIR) / fname
        if not fpath.exists():
            print(f"  [MISSING] {fname}")
            hash_ok = False
        else:
            actual_hash = compute_sha256(fpath)
            if actual_hash == expected_hash:
                print(f"  [VERIFIED] {fname}")
            else:
                print(f"  [TAMPERED] {fname} (Expected: {expected_hash}, Actual: {actual_hash})")
                hash_ok = False

    # Git status
    print("\n--- Git & Remote Status ---")
    try:
        remote_out = subprocess.check_output(["git", "remote", "-v"], cwd=ROOT_DIR, text=True).strip()
        branch_out = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT_DIR, text=True).strip()
        print(f"  Working Branch: {branch_out or '(detached/no commits)'}")
        print(f"  Remotes:\n    " + "\n    ".join(remote_out.splitlines()))
    except Exception as e:
        print(f"  Git query failed: {e}")

    # Compute progress
    total_req = sum(1 for t in tasks.values() if not t.get("is_optional", False))
    done_req = sum(1 for t in tasks.values() if not t.get("is_optional", False) and t.get("status") == "DONE")
    blocked_req = sum(1 for t in tasks.values() if not t.get("is_optional", False) and t.get("status") == "BLOCKED")

    pct = (done_req / total_req * 100) if total_req else 0.0
    print(f"\n--- Progress ---")
    print(f"Required Tasks: {done_req}/{total_req} ({pct:.1f}% complete, {blocked_req} blocked)")

    # Find next eligible tasks
    print("\n--- Next Dependency-Ready Eligible Tasks ---")
    eligible = []
    for tid, tinfo in tasks.items():
        if tinfo.get("status") in ("TODO", "IN_PROGRESS"):
            deps = tinfo.get("dependencies", [])
            deps_met = all(tasks.get(d, {}).get("status") == "DONE" for d in deps)
            if deps_met:
                eligible.append(tinfo)

    if eligible:
        for t in eligible[:5]:
            opt_tag = " [OPTIONAL]" if t.get("is_optional") else ""
            print(f"  * {t['id']}{opt_tag}: {t['title']} (Status: {t['status']})")
    else:
        print("  None. Check blockers or review completed tasks.")

    if getattr(args, "all", False):
        print("\n--- Full Task Inventory ---")
        for tid, tinfo in tasks.items():
            opt_tag = " (optional)" if tinfo.get("is_optional") else ""
            print(f"  [{tinfo['status']:11}] {tid:6}{opt_tag} : {tinfo['title']}")

    if not hash_ok:
        sys.exit(1)


def cmd_doctor(args):
    print("==================================================")
    print(" ClaimCraft BD — System Doctor & Capabilities")
    print("==================================================")

    def check_cmd(name, cmd):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
            print(f"  [OK] {name}: {out.splitlines()[0]}")
            return True
        except Exception:
            print(f"  [MISSING] {name}")
            return False

    runtimes = [
        ("Python", [sys.executable, "--version"]),
        ("Node.js", ["node", "-v"]),
        ("pnpm", [get_pnpm_cmd(), "-v"]),
        ("uv", ["uv", "--version"]),
        ("Git", ["git", "--version"]),
    ]

    print("\n--- Core Runtimes ---")
    all_ok = True
    for name, cmd in runtimes:
        if not check_cmd(name, cmd):
            all_ok = False

    print("\n--- Provider & AI Readiness ---")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    stt_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    print(f"  Gemini API Key: {'Configured' if gemini_key else 'Missing (synthetic/manual mode active)'}")
    print(f"  Supabase URL: {'Configured' if supabase_url else 'Missing (local/in-memory mode active)'}")
    print(f"  Supabase Key: {'Configured' if supabase_key else 'Missing'}")
    print(f"  Google STT Credentials: {'Configured' if stt_key else 'Missing (browser/fallback mode active)'}")

    print("\nDoctor check completed.")
    if not all_ok:
        sys.exit(1)


def cmd_bootstrap(args):
    print("Bootstrapping ClaimCraft BD workspace dependencies...")
    # Web install
    print("Installing workspace dependencies with pnpm...")
    subprocess.check_call([get_pnpm_cmd(), "install"], cwd=ROOT_DIR)

    # Backend sync
    backend_dir = ROOT_DIR / "services" / "backend"
    if backend_dir.exists() and (backend_dir / "pyproject.toml").exists():
        print("Syncing backend virtual environment with uv...")
        subprocess.check_call(["uv", "sync", "--all-extras"], cwd=backend_dir)

    print("Bootstrap completed.")


def cmd_check(args):
    scope = args.scope
    print(f"Running checks for scope: {scope}...")
    if scope == "foundation":
        print("\n--- 1. Document Integrity & Ledger ---")
        cmd_status(argparse.Namespace(all=False))

        print("\n--- 2. Bilingual i18n Message Parity Check ---")
        subprocess.check_call([sys.executable, str(ROOT_DIR / "scripts" / "verify_i18n.py")])

        print("\n--- 3. Backend Ruff Lint Check ---")
        backend_dir = ROOT_DIR / "services" / "backend"
        subprocess.check_call(["uv", "run", "ruff", "check", "app"], cwd=backend_dir)

        print("\n--- 3. Web Next.js Build / Typecheck ---")
        # Keep production checks separate from an active development server.
        check_env = {**os.environ, "EBARKI_NEXT_DIST_DIR": ".next-check"}
        subprocess.check_call(
            [get_pnpm_cmd(), "--filter", "@claimcraft/web", "build"],
            cwd=ROOT_DIR, env=check_env,
        )

        print("\n[SUCCESS] Foundation checks passed completely.")

    elif scope == "core":
        print("\n--- Backend Pytest Suites ---")
        backend_dir = ROOT_DIR / "services" / "backend"
        subprocess.check_call(["uv", "run", "pytest"], cwd=backend_dir)
        print("\n[SUCCESS] Core test checks passed completely.")

    elif scope == "release":
        print("\n--- Release Verification Suites ---")
        cmd_check(argparse.Namespace(scope="foundation"))
        cmd_check(argparse.Namespace(scope="core"))
        print("\n[SUCCESS] All release verification suites passed.")
    else:
        print(f"Unknown scope: {scope}", file=sys.stderr)
        sys.exit(1)


def cmd_contracts(args):
    print("Exporting OpenAPI and regenerating TypeScript contracts...")
    backend_dir = ROOT_DIR / "services" / "backend"
    subprocess.check_call(["uv", "run", "python", str(ROOT_DIR / "scripts" / "contracts.py")], cwd=backend_dir)
    print("Contracts generation verified.")


def cmd_seed_demo(args):
    print("Seeding synthetic demo case fixture...")
    backend_dir = ROOT_DIR / "services" / "backend"
    subprocess.check_call(["uv", "run", "python", str(ROOT_DIR / "scripts" / "seed_demo.py")], cwd=backend_dir)
    print("Demo seed complete.")


def free_port(port: int):
    """Frees port if held by a process to prevent EADDRINUSE on startup."""
    if is_windows():
        try:
            out = subprocess.check_output(
                f"netstat -ano | findstr :{port}", shell=True, text=True, stderr=subprocess.DEVNULL
            )
            for line in out.strip().splitlines():
                if "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    if pid and pid != "0":
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        except Exception:
            pass


def cmd_dev(args):
    print("==================================================")
    print(" ClaimCraft BD — Local Development Stack")
    print("==================================================")

    # 0. Free ports 8000 and 3000 if occupied by stale processes
    free_port(8000)
    free_port(3000)

    # 1. Clean stale Next.js build cache to avoid EINVAL on Windows
    next_dir = ROOT_DIR / "apps" / "web" / ".next"
    if next_dir.exists():
        import shutil
        shutil.rmtree(next_dir, ignore_errors=True)

    backend_dir = ROOT_DIR / "services" / "backend"
    web_dir = ROOT_DIR

    print("Starting Backend API on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=backend_dir,
    )

    print("Starting Web UI on http://localhost:3000...")
    pnpm_cmd = get_pnpm_cmd()
    web_proc = subprocess.Popen(
        [pnpm_cmd, "--filter", "@claimcraft/web", "dev"],
        cwd=web_dir,
    )

    print("\nClaimCraft BD dev services are running:")
    print("  - Backend API: http://127.0.0.1:8000")
    print("  - Web Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to terminate both services.\n")

    import time
    try:
        while True:
            b_ret = backend_proc.poll()
            w_ret = web_proc.poll()
            if b_ret is not None or w_ret is not None:
                if b_ret is not None:
                    print(f"\n[ALERT] Backend API terminated with exit code {b_ret}.")
                if w_ret is not None:
                    print(f"\n[ALERT] Web Frontend terminated with exit code {w_ret}.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down dev services...")
    finally:
        for p in (backend_proc, web_proc):
            try:
                p.terminate()
            except Exception:
                pass


def cmd_web(args):
    """Run a web workspace command through the cross-platform task runner."""
    if not args.web_args:
        raise SystemExit("Usage: python scripts/tasks.py web <pnpm command>")
    raise SystemExit(subprocess.call(
        [get_pnpm_cmd(), "--filter", "@claimcraft/web", *args.web_args], cwd=ROOT_DIR
    ))


def cmd_graphify(args):
    py_path_file = ROOT_DIR / "graphify-out" / ".graphify_python"
    if py_path_file.exists():
        py_exe = py_path_file.read_text(encoding="utf-8").strip()
    else:
        py_exe = sys.executable

    cmd = [py_exe, "-m", "graphify"] + (args.graphify_args or [])
    sys.exit(subprocess.call(cmd, cwd=ROOT_DIR))


def cmd_backend(args):
    """Run a uv command in the backend workspace."""
    if not args.backend_args:
        raise SystemExit("Usage: python scripts/tasks.py backend <uv command>")
    raise SystemExit(subprocess.call(["uv", *args.backend_args], cwd=ROOT_DIR / "services" / "backend"))


def main():
    parser = argparse.ArgumentParser(description="ClaimCraft BD task runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show task ledger and progress")
    status_parser.add_argument("--all", action="store_true", help="Print all tasks")
    status_parser.set_defaults(func=cmd_status)

    doctor_parser = subparsers.add_parser("doctor", help="Check system tools and provider readiness")
    doctor_parser.set_defaults(func=cmd_doctor)

    bootstrap_parser = subparsers.add_parser("bootstrap", help="Install pinned project dependencies")
    bootstrap_parser.set_defaults(func=cmd_bootstrap)

    check_parser = subparsers.add_parser("check", help="Run verification checks")
    check_parser.add_argument("--scope", choices=["foundation", "core", "release"], default="foundation")
    check_parser.set_defaults(func=cmd_check)

    contracts_parser = subparsers.add_parser("contracts", help="Export OpenAPI and regenerate TypeScript contracts")
    contracts_parser.set_defaults(func=cmd_contracts)

    seed_demo_parser = subparsers.add_parser("seed-demo", help="Idempotently seed synthetic demo case fixtures")
    seed_demo_parser.set_defaults(func=cmd_seed_demo)

    dev_parser = subparsers.add_parser("dev", help="Show instructions for running development servers")
    dev_parser.set_defaults(func=cmd_dev)

    web_parser = subparsers.add_parser("web", help="Run a command in the web workspace")
    web_parser.add_argument("web_args", nargs=argparse.REMAINDER)
    web_parser.set_defaults(func=cmd_web)

    backend_parser = subparsers.add_parser("backend", help="Run a uv command in the backend workspace")
    backend_parser.add_argument("backend_args", nargs=argparse.REMAINDER)
    backend_parser.set_defaults(func=cmd_backend)

    graphify_parser = subparsers.add_parser("graphify", help="Execute graphify CLI (query, update, path, explain)")
    graphify_parser.add_argument("graphify_args", nargs=argparse.REMAINDER, help="Arguments passed directly to graphify")
    graphify_parser.set_defaults(func=cmd_graphify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
