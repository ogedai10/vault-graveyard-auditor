"""Walk a vault and collect markdown notes, skipping junk directories."""
import os

DEFAULT_IGNORE = (".obsidian", ".git", "_templates", "node_modules", ".trash")


def collect(root, ignore=()):
    ignore_set = set(DEFAULT_IGNORE) | set(ignore)
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_set]
        for name in filenames:
            if name.lower().endswith(".md"):
                path = os.path.join(dirpath, name)
                try:
                    with open(path, encoding="utf-8") as f:
                        out.append((path, f.read()))
                except (OSError, UnicodeDecodeError):
                    continue
    return out
