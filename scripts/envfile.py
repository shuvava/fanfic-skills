"""Load KEY=value lines from a project's .env into os.environ — standard library only.

Imported by the scripts next to it (`from envfile import load_env`); they run as
`python3 <scripts>/x.py`, so this folder is on sys.path. Not a python-dotenv replacement: it reads
the simple subset a key file needs.

  # comment
  OPENROUTER_API_KEY=sk-or-...
  export NAME="value with spaces"   # `export` and matching quotes are accepted
  NAME='literal $value'

A variable already set in the environment wins — the shell overrides the file, never the reverse.
Values are never printed.
"""

import os
import re
from pathlib import Path

LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def parse(text):
    """Return {name: value} for the KEY=value lines of a .env text."""
    out = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = LINE.match(raw)
        if not m:
            continue
        name, value = m.groups()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = re.sub(r"\s+#.*$", "", value)  # unquoted: trailing " # comment" is not the value
        out[name] = value
    return out


def load_env(path=".env"):
    """Set variables from `path` (default ./.env — the project root, where the scripts run) that the
    environment does not already have. Returns the path read, or None if there was no file."""
    p = Path(path)
    if not p.is_file():
        return None
    for name, value in parse(p.read_text(encoding="utf-8")).items():
        os.environ.setdefault(name, value)
    return p
