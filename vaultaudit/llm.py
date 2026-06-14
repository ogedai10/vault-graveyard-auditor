"""Optional: ask Anthropic to judge a borderline note alive/dead. Never crashes the run."""
import os

_PROMPT = (
    "You judge whether a personal note carries the author's OWN opinion/take, or is just a "
    "captured summary/clip with no original thinking. Reply with exactly one word: ALIVE or "
    "DEAD, then a dash and a <=8 word reason. Note:\n\n"
)


def available():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def judge(text, model="claude-haiku-4-5-20251001"):
    """Return (bucket, reason) or None on any failure."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=model,
            max_tokens=40,
            messages=[{"role": "user", "content": _PROMPT + text[:4000]}],
        )
        reply = msg.content[0].text.strip()
        head = reply.split("-", 1)
        verdict = head[0].strip().lower()
        reason = head[1].strip() if len(head) > 1 else "llm call"
        if verdict.startswith("alive"):
            return ("alive", f"llm: {reason}")
        if verdict.startswith("dead"):
            return ("dead", f"llm: {reason}")
        return None
    except Exception:
        return None
