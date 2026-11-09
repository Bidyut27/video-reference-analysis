#!/usr/bin/env python3
"""Validate the Laughing Box AI files.

Checks every skill's SKILL.md frontmatter (Agent Skills spec), the Antigravity rule
frontmatter, all relative Markdown links, and that the generated Claude copies are fresh.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = (".git", ".hoplite", ".context", ".claude", "project-knowledge")
# generated copies, verified against their sources by build_claude_files.py --check
GENERATED = {os.path.join(ROOT, ".agents", "skills", "laughing-box-writer")}
errors = []


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else None), text


skill_dirs = [os.path.join(ROOT, ".agents", "skills", d) for d in sorted(os.listdir(os.path.join(ROOT, ".agents", "skills")))]
for sd in skill_dirs:
    rel = os.path.relpath(sd, ROOT)
    fm, text = frontmatter(os.path.join(sd, "SKILL.md"))
    if fm is None:
        errors.append(f"{rel}/SKILL.md: missing YAML frontmatter")
        continue
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    n = name.group(1).strip() if name else ""
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n) or len(n) > 64:
        errors.append(f"{rel}: name must be lowercase-hyphenated, at most 64 chars")
    elif n != os.path.basename(sd):
        errors.append(f"{rel}: name must match the folder name")
    if not desc or not (1 <= len(desc.group(1).strip()) <= 1024):
        errors.append(f"{rel}: description must be 1-1024 chars")
    if text.count("\n") > 500:
        errors.append(f"{rel}: SKILL.md should stay under 500 lines")

rules_dir = os.path.join(ROOT, ".agents", "rules")
for f in sorted(os.listdir(rules_dir)) if os.path.isdir(rules_dir) else []:
    fm, text = frontmatter(os.path.join(rules_dir, f))
    trig = re.search(r"^trigger:\s*(\S+)", fm or "", re.M)
    if not trig or trig.group(1) not in ("always_on", "model_decision", "glob", "manual"):
        errors.append(f".agents/rules/{f}: needs trigger always_on|model_decision|glob|manual")
    if len(text.encode()) > 24000:
        errors.append(f".agents/rules/{f}: over Antigravity's 24 KB rule limit")

for d, dirs, fs in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP and os.path.join(d, x) not in GENERATED]
    for f in fs:
        if not f.endswith(".md"):
            continue
        body = open(os.path.join(d, f), encoding="utf-8").read()
        for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
            if "://" in link:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(d, link))):
                errors.append(f"{os.path.relpath(os.path.join(d, f), ROOT)}: broken link {link}")

build = subprocess.run([sys.executable, os.path.join(ROOT, "laughing-box", "claude", "build_claude_files.py"), "--check"],
                       capture_output=True, text=True)
if build.returncode:
    errors.append("generated Claude files are stale; run python laughing-box/claude/build_claude_files.py:\n  "
                  + build.stdout.strip().replace("\n", "\n  ") + build.stderr.strip())

print("\n".join(errors) or "skills, rules, links and Claude copies OK")
sys.exit(1 if errors else 0)
