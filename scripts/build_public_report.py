#!/usr/bin/env python3
"""Build the public report from a temporary copy without editing tracked TeX.

Only transitively included TeX files and referenced figures are copied. A
missing, separately supplied university logo is omitted from the temporary
cover. On Linux, the temporary ctexart document uses TeX Live's Fandol fonts.
The original report sources and figures are never modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
GRAPHIC = re.compile(r"\\includegraphics\*?\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}")
CLASS = re.compile(r"\\documentclass\s*(?:\[([^\]]*)\]\s*)?\{ctexart\}")
BAD_LOG = re.compile(
    r"^!|Undefined control sequence|LaTeX Warning:.*undefined|"
    r"There were undefined references|Missing character:|Overfull "
    + re.escape(chr(92)) + r"[hv]box",
    re.MULTILINE,
)


def checked_source(relative: str, suffixes: tuple[str, ...]) -> Path:
    candidate = (REPORT / relative).resolve()
    if not candidate.is_relative_to(REPORT.resolve()):
        raise ValueError(f"Report resource leaves report directory: {relative}")
    options = [candidate] if candidate.suffix else [candidate.with_suffix(s) for s in suffixes]
    for option in options:
        if option.is_file():
            return option
    raise FileNotFoundError(f"Missing report resource: {relative}")


def copy_sources(destination: Path) -> tuple[int, int, bool, bool]:
    pending = [REPORT / "main.tex"]
    copied: set[Path] = set()
    graphics: set[Path] = set()
    logo_missing = not (REPORT / "figures/nku.png").is_file()
    linux_fonts = sys.platform.startswith("linux")
    while pending:
        source = pending.pop().resolve()
        if source in copied:
            continue
        text = source.read_text(encoding="utf-8")
        copied.add(source)
        if source == (REPORT / "main.tex").resolve():
            if logo_missing:
                text, count = re.subn(
                    r"\\includegraphics\*?\s*(?:\[[^\]]*\]\s*)?\{figures/nku\.png\}",
                    "", text,
                )
                if count != 1:
                    raise ValueError("Expected exactly one nku.png cover reference")
            if linux_fonts:
                match = CLASS.search(text)
                if match is None:
                    raise ValueError("Could not locate the ctexart document class")
                options = [o.strip() for o in (match.group(1) or "").split(",") if o.strip()]
                options = [o for o in options if not o.startswith("fontset=")]
                replacement = "\\documentclass[" + ",".join(options + ["fontset=fandol"]) + "]{ctexart}"
                text = text[:match.start()] + replacement + text[match.end():]
        target = destination / source.relative_to(REPORT.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        pending.extend(checked_source(name, (".tex",)) for name in INPUT.findall(text))
        graphics.update(checked_source(name, (".pdf", ".png", ".jpg", ".jpeg")) for name in GRAPHIC.findall(text))
    for figure in graphics:
        target = destination / figure.relative_to(REPORT.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(figure, target)
    return len(copied), len(graphics), logo_missing, linux_fonts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPORT / "main.pdf",
                        help="Destination PDF (default: project/report/main.pdf); relative paths use the current directory")
    args = parser.parse_args()
    if shutil.which("latexmk") is None:
        parser.error("latexmk is not on PATH; install TeX Live/XeLaTeX and the README dependencies")
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".pdf":
        parser.error("--output must end in .pdf")
    with tempfile.TemporaryDirectory(prefix="compiler-prelab-public-report-") as temp:
        temporary_report = Path(temp).resolve()
        counts = copy_sources(temporary_report)
        print(f"Copied {counts[0]} TeX sources and {counts[1]} figures; "
              f"missing logo omitted={counts[2]}, Linux Fandol fonts={counts[3]}", flush=True)
        command = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "main.tex"]
        result = subprocess.run(command, cwd=temporary_report)
        if result.returncode:
            print(f"latexmk failed with exit code {result.returncode}; existing destination preserved", file=sys.stderr)
            return result.returncode
        log = (temporary_report / "main.log").read_text(encoding="utf-8", errors="replace")
        bad = [line for line in log.splitlines() if BAD_LOG.search(line)]
        if bad:
            print("Report log requires inspection; existing destination preserved:", file=sys.stderr)
            print("\n".join(bad), file=sys.stderr)
            return 1
        pdf = temporary_report / "main.pdf"
        if not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
            print("latexmk did not produce a PDF; existing destination preserved", file=sys.stderr)
            return 1
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, output)
    print(f"PDF: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
