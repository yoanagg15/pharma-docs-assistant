"""Check bilingual documentation pairs, reciprocal links, and matching executable examples."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^\s)]+)\)")
COMMANDS = re.compile(r"^```(powershell|bash|sh|dotenv)\n(.*?)^```", re.M | re.S)


def check_documents():
    english_docs = sorted((ROOT / "docs").glob("*.md"))
    pairs = [(ROOT / "README.md", ROOT / "README.bg.md")]
    pairs.extend((path, ROOT / "docs/bg" / path.name) for path in english_docs)
    errors = []
    expected_bg = {bg for _, bg in pairs}
    for bg in (ROOT / "docs/bg").glob("*.md"):
        if bg not in expected_bg:
            errors.append(f"Bulgarian document has no English counterpart: {bg.relative_to(ROOT)}")
    for english, bulgarian in pairs:
        for path, counterpart in ((english, bulgarian), (bulgarian, english)):
            if not path.is_file():
                errors.append(f"Missing documentation: {path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding="utf-8")
            local_targets = []
            for target in LINK.findall(text):
                if ":" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                local_targets.append(resolved)
                if not resolved.exists():
                    errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
            if counterpart.resolve() not in local_targets:
                errors.append(f"Missing language link in {path.relative_to(ROOT)}")
        if english.is_file() and bulgarian.is_file():
            en_commands = COMMANDS.findall(english.read_text(encoding="utf-8"))
            bg_commands = COMMANDS.findall(bulgarian.read_text(encoding="utf-8"))
            if en_commands != bg_commands:
                errors.append(f"Executable examples differ: {english.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Bilingual documentation checks passed ({len(pairs)} document pairs).")


if __name__ == "__main__":
    check_documents()
