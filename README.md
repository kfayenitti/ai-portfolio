# KatherineNitti AI Portfolio

This repository holds my coursework, position statements, records of resistance, and project artifacts across the program.

Managed with the [Epistemic Stewardship Framework (ESF)](https://github.com/nmadrid27/Epistemic-Stewardship-Framework-ESF-).

## Quarter Question

What happens when generated code and AI-assisted imagery are used to streamline VFX production?

## Published work

- **AI 201 process book (blog):** [AI Creative Computing — Claude VEX Tool Generation](https://kfayenitti.wixsite.com/katherine-nitti-art/post/ai-creative-computing-claude-vex-tool-generation)

## Structure

After running the ESF Student Toolkit installer, the repository will contain:

- `projects/` — Course projects, organized by course
- `templates/` — ESF templates (position statements, records of resistance, AI use logs)
- `.claude/` — Toolkit configuration (if using Claude Code)
- `prompts/` — Plain-text prompts (if using other AI tools)

## Setup

If the toolkit is not yet installed, run:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/Epistemic-Stewardship-Framework-ESF-/main/student-toolkit/install.sh | bash
```

## On opening this repo in Claude Code

This repo’s `.claude/settings.json` runs a **SessionStart** hook that prints an ESF Companion status line when a session begins. The script is at [`.claude/hooks/esf-session-status.sh`](.claude/hooks/esf-session-status.sh): it only reads `companion-state.md` and writes that line to stderr. It does not modify files. Review the script before you rely on it in a new environment.
