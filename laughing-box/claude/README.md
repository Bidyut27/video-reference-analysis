# Laughing Box for Claude and Antigravity

Two skills, one set of rules, and a Claude Project setup. All copies are generated from single sources by `build_claude_files.py`, so they never drift apart.

| Skill | What it does | Needs |
|---|---|---|
| **laughing-box-episode** | Builds a full episode: 4K video with voices and captions, cover, posting copy | This repo + Python, ffmpeg, Kokoro model (Antigravity, Claude Code) |
| **laughing-box-writer** | Writes an episode: ideas, beats, shot list, script, cover design, AI image/video prompts, posting copy | Nothing (works anywhere, including claude.ai) |

## Antigravity (with Claude or Gemini models)

Open this repository folder as the workspace. Antigravity loads automatically:

- `AGENTS.md` and `GEMINI.md` (project instructions)
- `.agents/rules/laughing-box.md` (always-on rules)
- `.agents/skills/laughing-box-episode/` and `.agents/skills/laughing-box-writer/`

Pick a Claude model in the model menu if you like; the same files apply to every model. Then ask, for example: *"Give me the next Laughing Box topic"* or *"Go: make Grandpa vs. the Smart Speaker in 4K."*

Rendering needs, on your computer: Python 3.10+, `pip install pycairo numpy scipy kokoro-onnx soundfile librosa`, ffmpeg, and the Kokoro files `kokoro-v1.0.onnx` and `voices-v1.0.bin` from the [kokoro-onnx model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0). Tell the agent where you saved them.

## Claude Code

Open the repo and run `claude`. It reads `CLAUDE.md` and the skills in `.claude/skills/` (real copies, so this also works on Windows).

## claude.ai (web, desktop, mobile)

**1. Upload the skill** (needs code execution turned on in Settings):

1. Download [`laughing-box-writer.zip`](laughing-box-writer.zip). Don't unzip it.
2. In Claude, open **Customize → Skills**, upload the ZIP, and switch it on.

**2. Create a Project:**

1. Go to **Projects → New project**, name it "Laughing Box".
2. Paste everything in [`project-instructions.txt`](project-instructions.txt) into **Project instructions**.
3. Add the three files in [`project-knowledge/`](project-knowledge/) to **Project knowledge**: `series-bible.md`, `blueprint.md`, `prompt-kit.md`.

Every chat in that project then knows the cast, the formula and the rules. Ask *"5 new episode ideas"* or *"Go: write Leo vs. the Haircut."*

## Keeping things up to date

After a new episode, the agent adds it to the episode log in `.agents/skills/laughing-box-episode/references/series-bible.md`. Then run:

```bash
python laughing-box/claude/build_claude_files.py
```

This refreshes the Claude Code copies, the writer skill, `project-knowledge/` and the ZIP. Re-upload the ZIP and the knowledge files to claude.ai. `python .agents/check_skill.py` fails if anything is out of date.

Edit only these sources: `.agents/skills/laughing-box-episode/` (episode skill and references), `laughing-box/claude/laughing-box-writer/SKILL.md` (writer skill) and `laughing-box/production/blueprint.md`.
