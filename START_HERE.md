# Start Here

You just installed the ESF Companion.

---

## What got installed

**Claude Code install:**

```
.claude/
├── agents/esf-companion.md       ← AI companion identity
├── skills/                       ← Six skills (onboarding, project, git, verify, update, cognitive)
└── reference/                    ← Framework guide and disclosure protocol
templates/                        ← Blank forms for each ESF practice
prompts/                          ← Companion system prompt (`esf-companion.md`) for other AI tools
WORKFLOW.md                       ← Visual process diagram
```

---

## Your next 3 steps

**If you are on Claude Code:**

1. Open Claude Code in your project directory: `claude`
2. Run `/esf-onboarding` — takes about 5 minutes
3. Close Claude Code after onboarding and write your Position Statement before your first AI session

**If you are on Claude.ai, ChatGPT, Gemini, or another conversation tool:**

1. Open `prompts/esf-companion.md`
2. Copy everything below **System Prompt (copy everything below this line)**
3. Paste that block as your system prompt or first message

**If you are on Claude.ai Projects:**

1. Create a project in Claude.ai
2. Upload a filled-in copy of `templates/companion-state-template.md` and your brief from `projects/[course]/briefs/` as project knowledge
3. Set `prompts/esf-companion.md` as the system prompt

---

## What success looks like

After setup, the ESF Companion has one job: keep your thinking yours when you work with AI.

You will know it is working when:

- You write a Position Statement before AI sees your project, not after
- You can explain any part of your work without referencing what AI said
- Your Records of Resistance show decisions you made, not just output you accepted
- Your disclosure statement is honest and matches what actually happened

The Position Statement is the gate. Everything else follows from it.

---

## Customizing the Companion

**Silence mode** reduces how often the Companion speaks during a session. On Claude Code, run `/esf-onboarding` first; then set the preference in the companion state file onboarding creates (same structure as `templates/companion-state-template.md`):

```
## Preferences

- **silent_mode:** true
```

With silent mode on, the Companion suppresses proactive prompts, phase announcements, drift observations for low-significance moments, and unprompted check-ins. It still enforces the Position Statement gate, Five Questions, and disclosure requirement. Those cannot be silenced.

**If you are a student:** Silent mode is accepted, but a warning will appear once per session noting that blocking checkpoints remain active. If your instructor's brief requires full scaffolding, silent mode will be overridden automatically.

---

## Reference links


- **[prompts/esf-companion.md](prompts/esf-companion.md)** — System prompt for ChatGPT, Gemini, and Claude.ai
- **[WORKFLOW.md](WORKFLOW.md)** — Visual process diagram
- **[templates/](templates/)** — Blank forms: Position Statement, Record of Resistance, AI Use Log, Five Questions, Disclosure
- **[examples](https://github.com/nmadrid27/esf-companion/tree/main/examples)** — Filled samples across design, writing, research, and consulting
