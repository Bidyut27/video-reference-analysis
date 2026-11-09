#!/usr/bin/env python3
"""Build the Claude / Antigravity copies of the Laughing Box skills from their single sources.

  python laughing-box/claude/build_claude_files.py           # write everything
  python laughing-box/claude/build_claude_files.py --check   # exit 1 if anything is stale

Outputs:
  .claude/skills/laughing-box-episode/   real copy of .agents/skills/laughing-box-episode (Claude Code;
                                         a copy, not a symlink, so it also works on Windows)
  .agents/skills/laughing-box-writer/    writer skill for Antigravity (and Codex, Cursor, Gemini CLI)
  .claude/skills/laughing-box-writer/    the same for Claude Code
  laughing-box/claude/laughing-box-writer.zip    upload to claude.ai (Customize > Skills)
  laughing-box/claude/project-knowledge/         files to add to a claude.ai Project's knowledge
"""
import filecmp
import io
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
EPISODE_SKILL = os.path.join(ROOT, ".agents", "skills", "laughing-box-episode")
BIBLE = os.path.join(EPISODE_SKILL, "references", "series-bible.md")
PROMPT_KIT = os.path.join(EPISODE_SKILL, "references", "chat-prompt.md")
BLUEPRINT = os.path.join(ROOT, "laughing-box", "production", "blueprint.md")
WRITER_SRC = os.path.join(HERE, "laughing-box-writer", "SKILL.md")

# writer skill folder layout: relative path -> source file
WRITER_FILES = {
    "SKILL.md": WRITER_SRC,
    "references/series-bible.md": BIBLE,
    "references/blueprint.md": BLUEPRINT,
    "references/prompt-kit.md": PROMPT_KIT,
}
KNOWLEDGE_FILES = {
    "series-bible.md": BIBLE,
    "blueprint.md": BLUEPRINT,
    "prompt-kit.md": PROMPT_KIT,
}
DESC_LIMIT = 200  # claude.ai help-centre limit for uploaded skills


def tree_files(d):
    out = {}
    for base, _, fs in os.walk(d):
        for f in fs:
            if f.startswith(".") or "__pycache__" in base:
                continue
            p = os.path.join(base, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = p
    return out


def plan():
    """(destination folder, {relpath: source})."""
    return [
        (os.path.join(ROOT, ".claude", "skills", "laughing-box-episode"), tree_files(EPISODE_SKILL)),
        (os.path.join(ROOT, ".agents", "skills", "laughing-box-writer"), WRITER_FILES),
        (os.path.join(ROOT, ".claude", "skills", "laughing-box-writer"), WRITER_FILES),
        (os.path.join(HERE, "project-knowledge"), KNOWLEDGE_FILES),
    ]


def zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, src in sorted(WRITER_FILES.items()):
            info = zipfile.ZipInfo(f"laughing-box-writer/{rel}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(src, "rb") as f:
                z.writestr(info, f.read())
    return buf.getvalue()


def check_description():
    text = open(WRITER_SRC, encoding="utf-8").read()
    line = next(ln for ln in text.splitlines() if ln.startswith("description:"))
    n = len(line.split(":", 1)[1].strip())
    if n > DESC_LIMIT:
        sys.exit(f"laughing-box-writer description is {n} chars; claude.ai allows {DESC_LIMIT}")


def main():
    check_only = "--check" in sys.argv
    check_description()
    stale = []
    for dest, files in plan():
        if os.path.islink(dest):
            stale.append(f"{os.path.relpath(dest, ROOT)} is a symlink")
            if not check_only:
                os.unlink(dest)
        existing = tree_files(dest) if os.path.isdir(dest) else {}
        for rel in sorted(set(existing) - set(files)):
            stale.append(f"extra {os.path.relpath(existing[rel], ROOT)}")
            if not check_only:
                os.remove(existing[rel])
        for rel, src in files.items():
            out = os.path.join(dest, rel)
            if not (os.path.exists(out) and filecmp.cmp(src, out, shallow=False)):
                stale.append(f"stale {os.path.relpath(out, ROOT)}")
                if not check_only:
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copyfile(src, out)
    zpath = os.path.join(HERE, "laughing-box-writer.zip")
    data = zip_bytes()
    if not (os.path.exists(zpath) and open(zpath, "rb").read() == data):
        stale.append("stale laughing-box/claude/laughing-box-writer.zip")
        if not check_only:
            with open(zpath, "wb") as f:
                f.write(data)
    if check_only:
        print("\n".join(stale) or "claude files up to date")
        sys.exit(1 if stale else 0)
    print("\n".join(stale) or "nothing to update")


if __name__ == "__main__":
    main()
