#!/usr/bin/env python3
"""Validate the Laughing Box skill: SKILL.md frontmatter (Agent Skills spec) and relative links."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, ".agents", "skills", "laughing-box-episode")
errors = []

text = open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    errors.append("SKILL.md: missing YAML frontmatter")
else:
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name.group(1).strip()) or len(name.group(1).strip()) > 64:
        errors.append("name must be lowercase-hyphenated, at most 64 chars")
    elif name.group(1).strip() != os.path.basename(SKILL_DIR):
        errors.append("name must match the skill folder name")
    if not desc or not (1 <= len(desc.group(1).strip()) <= 1024):
        errors.append(f"description must be 1-1024 chars (got {len(desc.group(1).strip()) if desc else 0})")
if text.count("\n") > 500:
    errors.append("SKILL.md should stay under 500 lines")

for base, files in ((SKILL_DIR, ["SKILL.md", "references/series-bible.md", "references/chat-prompt.md"]),
                    (ROOT, ["AGENTS.md"])):
    for f in files:
        body = open(os.path.join(base, f), encoding="utf-8").read()
        for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
            if "://" in link:
                continue
            p = os.path.normpath(os.path.join(base, os.path.dirname(f), link))
            if not os.path.exists(p):
                errors.append(f"{f}: broken link {link}")

claude = os.path.join(ROOT, ".claude", "skills", "laughing-box-episode", "SKILL.md")
if not os.path.exists(claude):
    errors.append(".claude/skills/laughing-box-episode does not resolve to the skill")

print("\n".join(errors) or "skill OK")
sys.exit(1 if errors else 0)
