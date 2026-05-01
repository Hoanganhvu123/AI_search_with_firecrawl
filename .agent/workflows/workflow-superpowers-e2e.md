---
name: Superpowers E2E Autopilot
description: A master workflow that automates the entire lifecycle from Idea (brainstorming) -> Planning (writing-plans) -> Execution (TDD + Doing) -> Archive (Done). Integrates Superpowers skills and project-specific workflows.
---

# 🤖 Superpowers E2E Autopilot

> The ultimate automation loop. From a vague idea to a verified, archived implementation.

---

## 🛠️ The Pipeline States

| State | Folder | Skill / Workflow | Action |
|---|---|---|---|
| **CAPTURE** | `plan/ideas/` | `brainstorming` | Turn chat into a structured Idea file. |
| **PLAN** | `plan/doings/` | `writing-plans` | Convert Idea to a Checklist. Move file to `doings/`. |
| **EXECUTE** | `plan/doings/` | `tdd` | For each `[ ]`, write test, then code, then `[x]`. |
| **AUDIT** | `plan/doings/` | `workflow-audit.md` | Final quality and security scan. |
| **ARCHIVE** | `plan/done/` | `finishing-a-development-branch` | Move completed plan to `done/`. |

---

## 🧠 Step-by-Step Execution Logic

### Step 1: Idea Capture
- Trigger: `"Super-auto: [your idea]"`
- Action:
  1. Activate `brainstorming` skill.
  2. Create `plan/ideas/XX_[short_name].md`.
  3. Format: Name, Context, Requirements, Success Criteria.

### Step 2: From Idea to Doing
- Action:
  1. Activate `writing-plans` skill.
  2. Create a detailed implementation plan with checkboxes `[ ]`.
  3. Move file: `mv plan/ideas/XX.md plan/doings/XX.md`.

### Step 3: Checkbox-Driven Execution
- Action:
  - **Loop** through every `[ ]` in the file:
    1. Activate `test-driven-development` skill for the specific sub-task.
    2. Implement code.
    3. Verify with tests.
    4. Update file: Replace `[ ]` with `[x]` using `replace` tool.
    5. If a bug appears, create a file in `plan/doings/sub_doings/`.

### Step 4: Completion & Archiving
- Action:
  1. Once all `[ ]` are `[x]`, run `workflow-audit.md`.
  2. Move file: `mv plan/doings/XX.md plan/done/XX.md`.
  3. Report success to the user.

---

## 🚫 Critical Rules
- **NEVER** skip a checkbox.
- **ALWAYS** write a test before fixing a bug or adding a feature.
- **MOVE** files immediately when a state changes to keep the workspace clean.
- **SYNC** state: The markdown file is the "Source of Truth" for progress.
