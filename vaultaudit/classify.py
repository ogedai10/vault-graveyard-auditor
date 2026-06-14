"""Heuristic scoring: does a note carry the user's own take, or is it a dead capture?"""
import re

# Overlapping markers (e.g. "i disagree" also contains "disagree") double-count by design:
# more stance language = stronger signal. min(hits, 3) caps the payoff, so it can't run away.
STANCE_MARKERS = (
    "i think", "i believe", "my take", "my angle", "my view", "in my view",
    "my opinion", "imo", "i disagree", "disagree", "i'd argue", "the problem with",
    "what they miss", "what they get wrong", "gets it wrong", "wrong about",
    "i don't buy", "honestly", "hot take", "the real reason", "here's the thing",
    "what nobody",
)
TAKE_HEADING_RE = re.compile(
    r"^#{1,6}\s*(my take|angle|opinion|my view|thoughts|hot take)\b",
    re.IGNORECASE | re.MULTILINE,
)
_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_URL_RE = re.compile(r"https?://\S+")


def strip_noise(text):
    text = text.replace("\r\n", "\n")  # normalize so CRLF frontmatter/fences still match
    text = _FRONTMATTER_RE.sub("", text)
    text = _FENCE_RE.sub("", text)
    return text


def _content_lines(text):
    return [ln for ln in text.splitlines() if ln.strip()]


def quoted_ratio(text):
    lines = _content_lines(text)
    if not lines:
        return 0.0
    quoted = sum(1 for ln in lines if ln.lstrip().startswith(">"))
    return quoted / len(lines)


def original_words(text):
    words = 0
    for ln in _content_lines(text):
        s = ln.lstrip()
        if s.startswith(">") or s.startswith("#"):
            continue
        s = _URL_RE.sub("", s)
        words += len(s.split())
    return words


def stance_hits(text):
    low = text.lower()
    return sum(low.count(m) for m in STANCE_MARKERS)


def has_take_heading(text):
    return TAKE_HEADING_RE.search(text) is not None


def is_bare_link(text):
    has_url = _URL_RE.search(text) is not None
    return has_url and original_words(text) < 12


def word_count(text):
    return len(_URL_RE.sub("", text).split())


DEAD_BELOW = 25
ALIVE_AT = 55


def classify_note(text):
    body = strip_noise(text)
    qr = quoted_ratio(body)
    ow = original_words(body)
    sh = stance_hits(body)
    wc = word_count(body)
    bare = is_bare_link(body)
    take = has_take_heading(body)

    score = 0
    reasons = []
    if take:
        score += 40
        reasons.append("has a 'my take' style heading")
    if sh:
        score += min(sh, 3) * 15
        reasons.append(f"{sh} first-person take marker(s)")
    else:
        reasons.append("no first-person take")
    if ow >= 35:
        score += 15
        reasons.append("enough original prose")
    if qr >= 0.5:
        score -= 25
        reasons.append("mostly quoted source")
    if bare:
        score -= 30
        reasons.append("bare link, no commentary")
    if wc < 25 and sh == 0:
        score -= 15
        reasons.append("short stub")

    score = max(0, min(100, score))
    if score < DEAD_BELOW:
        bucket = "dead"
    elif score >= ALIVE_AT:
        bucket = "alive"
    else:
        bucket = "borderline"
    return {"score": score, "bucket": bucket, "reasons": reasons}
