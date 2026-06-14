"""CLI: python -m vaultaudit <vault> [--llm] [--report PATH] [--top N] [--ignore D ...] [--json]"""
import sys
import json
import argparse

from . import scan, classify, report, llm


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="vaultaudit",
        description="Score how many of your notes carry your own take (vs dead captures).",
    )
    parser.add_argument("vault", help="path to your markdown/Obsidian vault")
    parser.add_argument("--llm", action="store_true",
                        help="use Anthropic to sharpen borderline notes (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--report", default="graveyard-report.md",
                        help="path for the markdown report (default: ./graveyard-report.md)")
    parser.add_argument("--top", type=int, default=10, help="how many worst offenders to print")
    parser.add_argument("--ignore", nargs="*", default=[], help="extra directory names to skip")
    parser.add_argument("--json", action="store_true", help="print full verdicts as JSON")
    args = parser.parse_args(argv)

    notes = scan.collect(args.vault, ignore=tuple(args.ignore))
    if not notes:
        print(f"no .md notes found under {args.vault}", file=sys.stderr)
        return 1

    verdicts = []
    for path, text in notes:
        v = classify.classify_note(text)
        v["path"] = path
        verdicts.append(v)

    if args.llm:
        if not llm.available():
            print("  (--llm requested but unavailable: set ANTHROPIC_API_KEY and "
                  "pip install anthropic; using heuristic only)", file=sys.stderr)
        else:
            for v, (path, text) in zip(verdicts, notes):
                if v["bucket"] == "borderline":
                    res = llm.judge(text)
                    if res:
                        v["bucket"], reason = res
                        v["reasons"].append(reason)

    stats = report.summarize(verdicts)

    if args.json:
        print(json.dumps({"stats": stats, "verdicts": verdicts}, indent=2))
        return 0

    print(report.render_terminal(stats, verdicts, top=args.top))
    report.write_markdown(stats, verdicts, args.report)
    print(f"  full report written to {args.report}\n")
    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
