#!/usr/bin/env python3
"""Create fresh local TraceLog service secrets without printing their values."""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

SECRET_KEYS = ("REPLAY_SHARED_SECRET", "SERVICE_API_KEY")


def replace_secrets(content: str, values: dict[str, str]) -> str:
    lines = content.splitlines()
    found: set[str] = set()
    output: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in values:
            output.append(f"{key}={values[key]}")
            found.add(key)
        else:
            output.append(line)
    if output and output[-1]:
        output.append("")
    for key in SECRET_KEYS:
        if key not in found:
            output.append(f"{key}={values[key]}")
    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()
    path = Path(args.env_file)
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    values = {key: secrets.token_hex(32) for key in SECRET_KEYS}
    path.write_text(replace_secrets(content, values), encoding="utf-8")
    path.chmod(0o600)
    print("Generated fresh REPLAY_SHARED_SECRET and SERVICE_API_KEY; values were not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
