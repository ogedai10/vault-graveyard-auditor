"""Turn note verdicts into a graveyard score, a terminal summary, and a markdown report."""


def summarize(verdicts):
    total = len(verdicts)
    dead = sum(1 for v in verdicts if v["bucket"] == "dead")
    alive = sum(1 for v in verdicts if v["bucket"] == "alive")
    borderline = sum(1 for v in verdicts if v["bucket"] == "borderline")
    graveyard = round(100 * dead / total) if total else 0
    return {"total": total, "dead": dead, "alive": alive,
            "borderline": borderline, "graveyard_score": graveyard}


def _worst(verdicts, top):
    dead_first = sorted(verdicts, key=lambda v: v["score"])
    return dead_first[:top]


def render_terminal(stats, verdicts, top=10):
    lines = [
        "",
        f"  GRAVEYARD SCORE: {stats['graveyard_score']}% dead",
        f"  {stats['dead']} dead · {stats['borderline']} borderline · "
        f"{stats['alive']} alive  (of {stats['total']} notes)",
        "",
        "  worst offenders (lowest score first):",
    ]
    for v in _worst(verdicts, top):
        reason = v["reasons"][0] if v["reasons"] else ""
        lines.append(f"    [{v['score']:>3}] {v['path']}  — {reason}")
    lines.append("")
    return "\n".join(lines)


def write_markdown(stats, verdicts, path):
    lines = [
        "# Vault graveyard report",
        "",
        f"**Graveyard score: {stats['graveyard_score']}% dead** "
        f"({stats['dead']} dead, {stats['borderline']} borderline, "
        f"{stats['alive']} alive, {stats['total']} total)",
        "",
        "A note is *dead* when it is a capture with no take of your own. "
        "Fix the worst ones by adding what YOU think.",
        "",
        "## All notes (lowest score first)",
        "",
        "| score | bucket | note | why |",
        "| ----- | ------ | ---- | --- |",
    ]
    for v in sorted(verdicts, key=lambda v: v["score"]):
        why = "; ".join(v["reasons"]).replace("|", "\\|")
        note = str(v["path"]).replace("|", "\\|")
        lines.append(f"| {v['score']} | {v['bucket']} | {note} | {why} |")
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
