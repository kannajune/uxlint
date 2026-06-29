"""Command-line interface: `uxlint audit <url>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from uxlint import __version__
from uxlint.audit import audit
from uxlint.report import print_summary, write_annotated_image, write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uxlint",
        description="Lint a landing page for conversion (CRO) issues.",
    )
    parser.add_argument("--version", action="version", version=f"uxlint {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("audit", help="Audit a URL")
    a.add_argument("url", help="The page URL to audit")
    a.add_argument("-o", "--out", default="uxlint-report", help="Output directory")
    a.add_argument(
        "--viewport", choices=["desktop", "mobile"], default="desktop"
    )
    a.add_argument(
        "--backend",
        default="mock",
        help="Locator backend: 'mock' (no GPU) or 'locate-anything'.",
    )

    args = parser.parse_args(argv)

    if args.command == "audit":
        return _cmd_audit(args)
    parser.print_help()
    return 1


def _cmd_audit(args) -> int:
    try:
        result = audit(
            args.url, out_dir=args.out, viewport=args.viewport, backend=args.backend
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out = Path(args.out)
    write_json(result, out / "report.json")
    annotated = write_annotated_image(result, out / "annotated.png")
    print_summary(result)
    print(f"  artifacts: {out}/report.json  {annotated}\n")

    # Exit non-zero if any critical findings — handy for CI.
    return 1 if any(f.severity.value == "critical" for f in result.findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
