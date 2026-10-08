#!/usr/bin/env python3
"""PreToolUse hook (Bash): keep Databricks CLI calls inside this demo's footprint.

Blocks (exit 2, reason on stderr) a `databricks` command that:
  - uses a profile other than the configured one (-p / --profile)
  - names a workspace path outside the allowed prefixes
  - explicitly targets another catalog (--catalog-name, catalog_name, USE CATALOG)

Config: .claude/hooks/scope.json. It can't see SQL inside notebooks, app code, or files
passed with --json @file; CLAUDE.md covers those.
"""
import json
import os
import re
import shlex
import sys

WORKSPACE_PATH = re.compile(r"^(/Workspace)?/(Users/[^/]*@[^/]*|Shared|Repos)(/|$)")


def norm(path):
    path = path.rstrip("/")
    return path[len("/Workspace"):] if path.startswith("/Workspace/") else path


def block(reason):
    print(f"Blocked by .claude/hooks/guard_scope.py: {reason}", file=sys.stderr)
    sys.exit(2)


def main():
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    if "databricks" not in command:
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    with open(os.path.join(project, ".claude", "hooks", "scope.json")) as f:
        scope = json.load(f)

    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    for i, tok in enumerate(tokens):
        profile = None
        if tok in ("-p", "--profile") and i + 1 < len(tokens):
            profile = tokens[i + 1]
        elif tok.startswith("--profile="):
            profile = tok.split("=", 1)[1]
        if profile and profile != scope["profile"]:
            block(f"profile '{profile}' is not this demo's profile '{scope['profile']}'.")

    allowed = [norm(p) for p in scope["workspace_paths"]]
    for tok in tokens:
        for candidate in re.split(r"[=,]", tok):
            if WORKSPACE_PATH.match(candidate):
                path = norm(candidate)
                if not any(path == a or path.startswith(a + "/") for a in allowed):
                    block(f"workspace path '{candidate}' is outside this demo's allowed paths {allowed}.")

    catalog_refs = re.findall(
        r"(?:--catalog-name[= ]|\"?catalog_name\"?\s*[:=]\s*\"?|USE\s+CATALOG\s+`?)([A-Za-z0-9_]+)",
        command,
        flags=re.IGNORECASE,
    )
    for ref in catalog_refs:
        if ref != scope["catalog"]:
            block(f"catalog '{ref}' is not this demo's catalog '{scope['catalog']}'.")


if __name__ == "__main__":
    main()
