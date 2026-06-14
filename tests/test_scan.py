import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vaultaudit import scan


def _make_vault():
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, ".obsidian"))
    os.makedirs(os.path.join(root, "sub"))
    with open(os.path.join(root, "a.md"), "w") as f:
        f.write("note a")
    with open(os.path.join(root, "sub", "b.md"), "w") as f:
        f.write("note b")
    with open(os.path.join(root, "notes.txt"), "w") as f:
        f.write("not markdown")
    with open(os.path.join(root, ".obsidian", "c.md"), "w") as f:
        f.write("config note")
    return root


def test_scan_collects_only_markdown_recursively():
    root = _make_vault()
    found = scan.collect(root)
    names = sorted(os.path.basename(p) for p, _ in found)
    assert names == ["a.md", "b.md"]


def test_scan_skips_ignored_dirs():
    root = _make_vault()
    found = scan.collect(root)
    assert all(".obsidian" not in p for p, _ in found)


def test_scan_extra_ignore_dir():
    root = _make_vault()
    found = scan.collect(root, ignore=("sub",))
    names = sorted(os.path.basename(p) for p, _ in found)
    assert names == ["a.md"]


def test_scan_returns_text_content():
    root = _make_vault()
    found = dict((os.path.basename(p), t) for p, t in scan.collect(root))
    assert found["a.md"] == "note a"


if __name__ == "__main__":
    test_scan_collects_only_markdown_recursively()
    test_scan_skips_ignored_dirs()
    test_scan_extra_ignore_dir()
    test_scan_returns_text_content()
    print("OK: scan")
