import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vaultaudit import report


def _verdicts():
    return [
        {"path": "a.md", "score": 80, "bucket": "alive", "reasons": ["enough original prose"]},
        {"path": "b.md", "score": 10, "bucket": "dead", "reasons": ["bare link, no commentary"]},
        {"path": "c.md", "score": 5, "bucket": "dead", "reasons": ["mostly quoted source"]},
        {"path": "d.md", "score": 40, "bucket": "borderline", "reasons": ["no first-person take"]},
    ]


def test_summarize_counts_and_graveyard_score():
    s = report.summarize(_verdicts())
    assert s["total"] == 4
    assert s["dead"] == 2
    assert s["alive"] == 1
    assert s["borderline"] == 1
    assert s["graveyard_score"] == 50


def test_summarize_empty_is_zero_not_crash():
    s = report.summarize([])
    assert s["total"] == 0
    assert s["graveyard_score"] == 0


def test_render_terminal_has_score_and_offenders():
    s = report.summarize(_verdicts())
    out = report.render_terminal(s, _verdicts(), top=2)
    assert "50%" in out
    assert "b.md" in out


def test_write_markdown_creates_file_with_score():
    s = report.summarize(_verdicts())
    path = os.path.join(tempfile.mkdtemp(), "graveyard-report.md")
    report.write_markdown(s, _verdicts(), path)
    body = open(path, encoding="utf-8").read()
    assert "50%" in body
    assert "b.md" in body
    assert "a.md" in body


def test_write_markdown_escapes_pipes_in_path():
    s = report.summarize([])
    verdicts = [{"path": "notes/a|b.md", "score": 10, "bucket": "dead",
                 "reasons": ["has a | pipe"]}]
    path = os.path.join(tempfile.mkdtemp(), "graveyard-report.md")
    report.write_markdown(s, verdicts, path)
    row = [ln for ln in open(path, encoding="utf-8").read().splitlines()
           if "a\\|b.md" in ln][0]
    # the row's cell count must stay 4 (6 pipes incl. edges), not blown apart by raw pipes
    assert row.count("|") - row.count("\\|") == 5


if __name__ == "__main__":
    test_summarize_counts_and_graveyard_score()
    test_summarize_empty_is_zero_not_crash()
    test_render_terminal_has_score_and_offenders()
    test_write_markdown_creates_file_with_score()
    test_write_markdown_escapes_pipes_in_path()
    print("OK: report")
