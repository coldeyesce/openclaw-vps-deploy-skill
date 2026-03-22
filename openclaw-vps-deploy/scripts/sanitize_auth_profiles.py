#!/usr/bin/env python3
import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: sanitize_auth_profiles.py <auth-profiles.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    before_profiles = 0
    removed = []

    if isinstance(data, dict) and isinstance(data.get("profiles"), dict):
        before_profiles = len(data["profiles"])
        kept = {}
        for key, value in data["profiles"].items():
            if str(key).startswith("openai:"):
                removed.append(key)
                continue
            kept[key] = value
        data["profiles"] = kept

    if isinstance(data, dict) and isinstance(data.get("order"), list):
        data["order"] = [x for x in data["order"] if not str(x).startswith("openai:")]

    if isinstance(data, dict) and isinstance(data.get("default"), dict):
        data["default"] = {k: v for k, v in data["default"].items() if k != "openai"}

    if isinstance(data, dict) and "openai" in data and "openai-codex" in data:
        del data["openai"]
        removed.append("top-level:openai")

    backup = path.with_name(path.name + ".bak")
    shutil.copy2(path, backup)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    after_profiles = len(data.get("profiles", {})) if isinstance(data, dict) else 0
    print(json.dumps({
        "file": str(path),
        "backup": str(backup),
        "profiles_before": before_profiles,
        "profiles_after": after_profiles,
        "removed": removed,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
