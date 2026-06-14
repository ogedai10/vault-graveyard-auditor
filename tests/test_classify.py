import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vaultaudit import classify as c


def test_strip_frontmatter_removes_yaml_block():
    text = "---\ntitle: x\ntags: [a]\n---\n\nreal body here"
    out = c.strip_noise(text)
    assert "title: x" not in out
    assert "real body here" in out


def test_strip_noise_removes_code_fences():
    text = "before\n```python\nprint('hi')\n```\nafter"
    out = c.strip_noise(text)
    assert "print('hi')" not in out
    assert "before" in out and "after" in out


def test_quoted_ratio_counts_blockquote_lines():
    text = "> quoted one\n> quoted two\nmy own line"
    assert abs(c.quoted_ratio(text) - (2 / 3)) < 0.01


def test_quoted_ratio_zero_when_no_content():
    assert c.quoted_ratio("") == 0.0


def test_strip_frontmatter_handles_crlf():
    text = "---\r\nsummary: i think this is great\r\n---\r\n> just a clip"
    out = c.strip_noise(text)
    assert "i think this is great" not in out  # CRLF frontmatter must be stripped


def test_stance_hits_overlap_is_intentional():
    # "i disagree" also contains "disagree" -> 2 by design (capped later by min(hits,3))
    assert c.stance_hits("i disagree with this") == 2


def test_stance_hits_counts_first_person_markers():
    text = "i think this is wrong. honestly, my take is different."
    assert c.stance_hits(text) == 3


def test_has_take_heading_detects_my_take_section():
    assert c.has_take_heading("## My Take\nstuff") is True
    assert c.has_take_heading("## Summary\nstuff") is False


def test_is_bare_link_true_for_title_plus_url_only():
    text = "# Cool article\nhttps://example.com/post"
    assert c.is_bare_link(text) is True


def test_is_bare_link_false_when_real_prose_present():
    text = "# Cool article\nhttps://example.com/post\ni disagree with the whole premise here, it misses the point about shipping"
    assert c.is_bare_link(text) is False


def test_classify_quoted_no_stance_is_dead():
    text = "# Notes\n> clipped line one\n> clipped line two\n> clipped line three"
    v = c.classify_note(text)
    assert v["bucket"] == "dead"
    assert any("quoted" in r.lower() for r in v["reasons"])


def test_classify_take_heading_with_prose_is_alive():
    text = ("## My Take\n"
            "i think the whole framing is off. the real win is forcing an opinion "
            "out of every source, not just storing the source. that is the part people skip.")
    v = c.classify_note(text)
    assert v["bucket"] == "alive"


def test_classify_bare_link_is_dead():
    text = "# Cool post\nhttps://example.com/x"
    v = c.classify_note(text)
    assert v["bucket"] == "dead"
    assert any("bare link" in r.lower() for r in v["reasons"])


def test_classify_two_stance_markers_with_prose_is_alive():
    text = ("honestly this is wrong. i disagree with the core claim. "
            "the thing they miss is that the system is the pipeline, not the app, "
            "and that changes how you should set the whole vault up from day one.")
    v = c.classify_note(text)
    assert v["bucket"] == "alive"


def test_classify_short_stub_is_dead():
    text = "# todo read this later"
    v = c.classify_note(text)
    assert v["bucket"] == "dead"


def test_classify_score_is_clamped_0_100():
    text = "## My Take\n" + ("i think i disagree my angle honestly " * 10) + ("word " * 60)
    v = c.classify_note(text)
    assert 0 <= v["score"] <= 100


def test_classify_strips_frontmatter_before_scoring():
    text = "---\nsummary: i think this is great\n---\n> just a clip\n> another clip"
    v = c.classify_note(text)
    assert v["bucket"] == "dead"


if __name__ == "__main__":
    test_strip_frontmatter_removes_yaml_block()
    test_strip_noise_removes_code_fences()
    test_quoted_ratio_counts_blockquote_lines()
    test_quoted_ratio_zero_when_no_content()
    test_strip_frontmatter_handles_crlf()
    test_stance_hits_overlap_is_intentional()
    test_stance_hits_counts_first_person_markers()
    test_has_take_heading_detects_my_take_section()
    test_is_bare_link_true_for_title_plus_url_only()
    test_is_bare_link_false_when_real_prose_present()
    test_classify_quoted_no_stance_is_dead()
    test_classify_take_heading_with_prose_is_alive()
    test_classify_bare_link_is_dead()
    test_classify_two_stance_markers_with_prose_is_alive()
    test_classify_short_stub_is_dead()
    test_classify_score_is_clamped_0_100()
    test_classify_strips_frontmatter_before_scoring()
    print("OK: classify signals")
