#!/usr/bin/env python3
"""
Universal AI Memory Sync — Cross-platform AI memory synchronization tool
通用 AI 记忆同步工具 — 跨平台跨设备同步 AI 记忆文件

Supported agents / 支持的 AI 平台:
  workbuddy   WorkBuddy (.workbuddy/memory/ + workspace scans)
  cursor      Cursor IDE (.cursor/rules, CLAUDE.md, .cursorrules)
  openclaw    OpenClaw (MEMORY.md, TOOLS.md, AGENTS.md, memory/*.md)
  windsurf    Windsurf (.windsurf/rules, MEMORY.md)
  generic     Any directory — pass --memory-dir explicitly
  all         Sync all detected agents at once

Usage / 用法:
  python memory_sync.py setup [--repo URL] [--token TOKEN]
  python memory_sync.py push  [--agent AGENT]
  python memory_sync.py pull  [--agent AGENT]
  python memory_sync.py status
  python memory_sync.py agents   # list detected agents on this machine

Project / 项目地址: https://github.com/SuperCrzy/workbuddy-memory-sync
"""

import sys
import os
import json
import subprocess
import shutil
import platform
from pathlib import Path
from datetime import datetime

# ── Windows console UTF-8 fix ────────────────────────────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Global paths (all dynamic, no hardcoding) ────────────────
HOME           = Path.home()
WORKBUDDY_DIR  = HOME / ".workbuddy"
CONFIG_PATH    = WORKBUDDY_DIR / "memory-sync-config.json"
REPO_CACHE     = WORKBUDDY_DIR / "memory-sync-repo"

# ── Agent definitions ────────────────────────────────────────

def get_workspace_root() -> Path:
    """Detect WorkBuddy workspace root directory."""
    env = os.environ.get("WORKBUDDY_WORKSPACE_ROOT")
    if env:
        return Path(env)
    candidates = [
        HOME / "WorkBuddy",
        HOME / "workbuddy",
        Path("C:/Users") / os.environ.get("USERNAME", "user") / "WorkBuddy",
    ]
    for c in candidates:
        if c.exists():
            return c
    return HOME / "WorkBuddy"


def discover_agent_dirs(agent: str) -> dict:
    """
    Return {repo_subpath: local_path} for the given agent name.
    repo_subpath is where files land in the GitHub repo.
    """
    result = {}

    if agent in ("workbuddy", "all"):
        # User-level memory
        user_mem = WORKBUDDY_DIR / "memory"
        if user_mem.exists() and list(user_mem.glob("*.md")):
            result["agents/workbuddy/__user__"] = user_mem
        # Workspace-level memory
        ws_root = get_workspace_root()
        if ws_root.exists():
            for ws_dir in sorted(ws_root.iterdir()):
                if not ws_dir.is_dir():
                    continue
                mem_path = ws_dir / ".workbuddy" / "memory"
                if mem_path.exists() and list(mem_path.glob("*.md")):
                    result[f"agents/workbuddy/workspaces/{ws_dir.name}"] = mem_path

    if agent in ("cursor", "all"):
        # .cursor/rules directory
        cursor_rules = HOME / ".cursor" / "rules"
        if cursor_rules.exists() and list(cursor_rules.glob("*")):
            result["agents/cursor/rules"] = cursor_rules
        # Project-level CLAUDE.md / .cursorrules (scan common project dirs)
        for proj_root in [HOME / "projects", HOME / "code", HOME / "dev", HOME / "Documents"]:
            if proj_root.exists():
                for proj in list(proj_root.iterdir())[:20]:  # limit scan depth
                    if not proj.is_dir():
                        continue
                    for fname in ["CLAUDE.md", ".cursorrules", "CURSOR.md"]:
                        f = proj / fname
                        if f.exists():
                            result[f"agents/cursor/projects/{proj.name}/{fname}"] = f

    if agent in ("openclaw", "all"):
        # OpenClaw memory files — scan common project locations
        for search_root in [HOME / "WorkBuddy", HOME / "projects", HOME / "code", HOME]:
            if not search_root.exists():
                continue
            for subdir in list(search_root.iterdir())[:50]:
                if not subdir.is_dir():
                    continue
                collected = {}
                for fname in ["MEMORY.md", "TOOLS.md", "AGENTS.md"]:
                    f = subdir / fname
                    if f.exists():
                        collected[fname] = f
                mem_dir = subdir / "memory"
                if mem_dir.exists() and list(mem_dir.glob("*.md")):
                    collected["memory/"] = mem_dir
                if len(collected) >= 2:  # at least 2 OpenClaw files = likely OpenClaw project
                    for fname, fpath in collected.items():
                        key = f"agents/openclaw/{subdir.name}/{fname}"
                        result[key] = fpath

    if agent in ("windsurf", "all"):
        ws_rules = HOME / ".windsurf" / "rules"
        if ws_rules.exists():
            result["agents/windsurf/rules"] = ws_rules
        ws_mem = HOME / ".windsurf" / "memory"
        if ws_mem.exists() and list(ws_mem.glob("*.md")):
            result["agents/windsurf/memory"] = ws_mem

    if agent == "generic":
        mem_dir_env = os.environ.get("MEMORY_DIR") or os.environ.get("WORKBUDDY_MEMORY_DIR")
        if mem_dir_env:
            p = Path(mem_dir_env)
            if p.exists():
                result["agents/generic/memory"] = p
        else:
            log("[WARN] --agent generic requires MEMORY_DIR env var to be set.")
            log("  Example: MEMORY_DIR=/path/to/memory python memory_sync.py push --agent generic")

    return result


# ── Utilities ────────────────────────────────────────────────

def log(msg: str):
    print(msg, flush=True)

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        log("[ERROR] No config found. Please run setup first:")
        log("  python memory_sync.py setup --repo <URL> --token <TOKEN>")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    log(f"[OK] Config saved to {CONFIG_PATH}")

def build_auth_url(repo_url: str, token: str) -> str:
    if "github.com" in repo_url and token:
        return repo_url.replace("https://", f"https://{token}@")
    return repo_url

def run_git(args: list, cwd: str, silent: bool = False) -> tuple:
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ.copy()
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def ensure_repo(config: dict) -> Path:
    repo_url = config["repo_url"]
    token    = config.get("token", "")
    auth_url = build_auth_url(repo_url, token)

    if not (REPO_CACHE / ".git").exists():
        log(f"[INFO] Cloning repo to {REPO_CACHE} ...")
        REPO_CACHE.parent.mkdir(parents=True, exist_ok=True)
        code, out, err = run_git(["clone", auth_url, str(REPO_CACHE)], cwd=str(HOME))
        if code != 0:
            log(f"[ERROR] Clone failed: {err}")
            log("Check your repo URL and Token, and ensure the repo has at least one commit.")
            sys.exit(1)
        log("[OK] Clone successful")
    else:
        run_git(["remote", "set-url", "origin", auth_url], cwd=str(REPO_CACHE), silent=True)

    return REPO_CACHE

def get_current_branch(repo_dir: Path) -> str:
    code, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_dir))
    return out if (code == 0 and out) else "main"

def get_hostname() -> str:
    try:
        return platform.node() or "unknown"
    except Exception:
        return "unknown"

def parse_args(args: list) -> dict:
    """Simple key-value arg parser: --key value"""
    parsed = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            parsed[args[i][2:]] = args[i + 1]
            i += 2
        else:
            parsed[f"_pos_{i}"] = args[i]
            i += 1
    return parsed


# ── Commands ─────────────────────────────────────────────────

def cmd_setup(args: list):
    p = parse_args(args)
    repo_url = p.get("repo")
    token    = p.get("token")

    if not repo_url:
        log("Enter your GitHub private repo URL")
        log("Example: https://github.com/yourname/ai-memory")
        repo_url = input("> ").strip()
    if not token:
        log("Enter your GitHub Personal Access Token (needs 'repo' scope)")
        token = input("> ").strip()

    config = {"repo_url": repo_url, "token": token}
    save_config(config)

    log("\n[INFO] Verifying connection...")
    ensure_repo(config)
    log(f"\n[OK] Setup complete!")
    log(f"  Local repo cache : {REPO_CACHE}")
    log(f"  Workspace root   : {get_workspace_root()}")
    log("\nRun: python memory_sync.py push")


def _copy_dir_to_repo(src_dir: Path, dest_dir: Path) -> int:
    """Copy all .md files from src_dir to dest_dir. Returns count."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for f in sorted(src_dir.glob("*.md")):
        shutil.copy2(f, dest_dir / f.name)
        copied += 1
    return copied

def _copy_file_to_repo(src_file: Path, dest_dir: Path) -> int:
    """Copy a single file to dest_dir. Returns 1 if copied."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_dir / src_file.name)
    return 1


def cmd_push(args: list):
    p = parse_args(args)
    agent    = p.get("agent", "workbuddy")
    config   = load_config()
    repo_dir = ensure_repo(config)

    agent_dirs = discover_agent_dirs(agent)
    if not agent_dirs:
        log(f"[WARN] No memory directories found for agent: {agent}")
        return

    log(f"[INFO] Syncing agent={agent}, found {len(agent_dirs)} source(s)...")

    total_copied = 0
    for repo_key, local_path in agent_dirs.items():
        dest = repo_dir / repo_key
        if local_path.is_dir():
            copied = _copy_dir_to_repo(local_path, dest)
        else:
            copied = _copy_file_to_repo(local_path, dest.parent)
        if copied > 0:
            log(f"  {repo_key}: {copied} file(s)")
            total_copied += copied

    if total_copied == 0:
        log("[INFO] Nothing to sync")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname  = get_hostname()

    run_git(["add", "."], cwd=str(repo_dir))
    code, out, err = run_git(
        ["commit", "-m", f"sync({agent}): {timestamp} from {hostname} ({total_copied} files)"],
        cwd=str(repo_dir)
    )
    if code != 0 and "nothing to commit" in (out + err).lower():
        log("[OK] No changes since last sync")
        return

    branch = get_current_branch(repo_dir)
    code, out, err = run_git(["push", "origin", branch], cwd=str(repo_dir))
    if code != 0:
        code, out, err = run_git(["push", "--set-upstream", "origin", branch], cwd=str(repo_dir))

    if code == 0:
        log(f"\n[OK] Push successful! Synced {total_copied} file(s) from {len(agent_dirs)} source(s)")
    else:
        log(f"[ERROR] Push failed: {err}")
        sys.exit(1)


def _copy_newer(src_dir: Path, dest_dir: Path) -> int:
    """Copy files from src to dest only if src is newer. Returns count."""
    copied = 0
    for f in sorted(src_dir.glob("*.md")):
        dest_file = dest_dir / f.name
        if dest_file.exists() and dest_file.stat().st_mtime >= f.stat().st_mtime:
            continue
        shutil.copy2(f, dest_file)
        copied += 1
    return copied


def cmd_pull(args: list):
    p = parse_args(args)
    agent    = p.get("agent", "workbuddy")
    config   = load_config()
    repo_dir = ensure_repo(config)

    log(f"[INFO] Pulling latest memory from GitHub (agent={agent})...")
    branch = get_current_branch(repo_dir)
    code, out, err = run_git(["pull", "origin", branch], cwd=str(repo_dir))
    if code != 0:
        log(f"[WARN] Pull issue: {err}")
        log("If this is the first use, push from another device first.")
        return

    total_copied = 0
    agents_dir = repo_dir / "agents"
    if not agents_dir.exists():
        log("[INFO] No synced data found in repo yet.")
        return

    if agent == "all":
        scan_agents = [d.name for d in agents_dir.iterdir() if d.is_dir()]
    else:
        scan_agents = [agent]

    for ag in scan_agents:
        ag_dir = agents_dir / ag
        if not ag_dir.exists():
            continue

        if ag == "workbuddy":
            # User-level
            src_user = ag_dir / "__user__"
            if src_user.exists():
                dest = WORKBUDDY_DIR / "memory"
                dest.mkdir(parents=True, exist_ok=True)
                copied = _copy_newer(src_user, dest)
                if copied:
                    log(f"  workbuddy/__user__: {copied} file(s) updated")
                    total_copied += copied
            # Workspace-level
            ws_src = ag_dir / "workspaces"
            if ws_src.exists():
                ws_root = get_workspace_root()
                for ws_id_dir in sorted(ws_src.iterdir()):
                    if not ws_id_dir.is_dir():
                        continue
                    ws_dest = ws_root / ws_id_dir.name / ".workbuddy" / "memory"
                    if not (ws_root / ws_id_dir.name).exists():
                        continue  # skip workspaces not present on this machine
                    ws_dest.mkdir(parents=True, exist_ok=True)
                    copied = _copy_newer(ws_id_dir, ws_dest)
                    if copied:
                        log(f"  workbuddy/workspaces/{ws_id_dir.name}: {copied} file(s) updated")
                        total_copied += copied

        elif ag == "cursor":
            rules_src = ag_dir / "rules"
            if rules_src.exists():
                dest = HOME / ".cursor" / "rules"
                dest.mkdir(parents=True, exist_ok=True)
                for f in rules_src.glob("*"):
                    shutil.copy2(f, dest / f.name)
                    total_copied += 1
                    log(f"  cursor/rules/{f.name}: updated")

        elif ag in ("openclaw", "windsurf", "generic"):
            # Generic restore: recreate directory structure
            for item in ag_dir.rglob("*.md"):
                rel = item.relative_to(ag_dir)
                # Restore to a local .ai-memory/<agent>/<rel> directory
                dest_file = HOME / ".ai-memory" / ag / rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                if not dest_file.exists() or dest_file.stat().st_mtime < item.stat().st_mtime:
                    shutil.copy2(item, dest_file)
                    log(f"  {ag}/{rel}: updated")
                    total_copied += 1

    if total_copied > 0:
        log(f"\n[OK] Pull complete! Updated {total_copied} file(s)")
    else:
        log("[OK] Already up to date")


def cmd_agents(args: list):
    """List all detected agents and their memory directories on this machine."""
    log(f"[INFO] Scanning for AI agents on this machine...\n")
    all_dirs = discover_agent_dirs("all")
    if not all_dirs:
        log("  No agent memory directories detected.")
        return
    current_prefix = ""
    for repo_key, local_path in sorted(all_dirs.items()):
        agent_name = repo_key.split("/")[1]
        if agent_name != current_prefix:
            log(f"\n[{agent_name.upper()}]")
            current_prefix = agent_name
        if local_path.is_dir():
            files = list(local_path.glob("*.md"))
            log(f"  {repo_key.split('/', 2)[-1]}: {len(files)} .md file(s)  ({local_path})")
        else:
            log(f"  {repo_key.split('/', 2)[-1]}: 1 file  ({local_path})")


def cmd_status(args: list):
    if not CONFIG_PATH.exists():
        log("[ERROR] Not configured. Run: python memory_sync.py setup")
        return

    config = load_config()
    log(f"Repo URL    : {config['repo_url']}")
    log(f"Local cache : {REPO_CACHE}")
    log(f"Platform    : {platform.system()} {platform.release()}")
    log(f"Hostname    : {get_hostname()}")

    if (REPO_CACHE / ".git").exists():
        code, out, _ = run_git(["log", "--oneline", "-5"], cwd=str(REPO_CACHE))
        if code == 0 and out:
            log("\nLast 5 syncs:")
            for line in out.split("\n"):
                log(f"  {line}")

    log("\nDetected memory sources:")
    all_dirs = discover_agent_dirs("all")
    if not all_dirs:
        log("  (none found)")
    else:
        for repo_key, local_path in sorted(all_dirs.items()):
            if local_path.is_dir():
                files = list(local_path.glob("*.md"))
                log(f"  {repo_key}: {len(files)} file(s)  ({local_path})")
            else:
                log(f"  {repo_key}: 1 file  ({local_path})")


# ── Entry point ───────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd  = sys.argv[1].lower()
    rest = sys.argv[2:]

    commands = {
        "setup":  cmd_setup,
        "push":   cmd_push,
        "pull":   cmd_pull,
        "status": cmd_status,
        "agents": cmd_agents,
    }

    if cmd not in commands:
        log(f"[ERROR] Unknown command: {cmd}")
        log(f"Available: {' / '.join(commands.keys())}")
        sys.exit(1)

    commands[cmd](rest)


if __name__ == "__main__":
    main()
