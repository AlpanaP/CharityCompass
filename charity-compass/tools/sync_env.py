"""Utility for syncing environment variables across deployment targets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def load_env_file(path: Path) -> dict[str, str]:
    """Load KEY=VALUE pairs from a .env-style file."""
    env: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def dump_env(env: dict[str, str]) -> str:
    return json.dumps(env, indent=2, sort_keys=True)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sync env variables to remote targets")
    parser.add_argument("env_file", type=Path, help="Path to the source .env file")
    args = parser.parse_args(list(argv) if argv is not None else None)

    env = load_env_file(args.env_file)
    # TODO(alpana): integrate with Vercel/Render APIs.
    print(dump_env(env))


if __name__ == "__main__":  # pragma: no cover
    main()
