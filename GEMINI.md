# Project Instructions

This project mandates the use of the **Superpowers** development methodology enhanced with **Hermes Agent** self-learning patterns.

## 🚀 Mandatory Workflows
- **Super-Autopilot Mode**: Use when requested with "Super-auto: [idea]". Follows `.agent/workflows/workflow-superpowers-e2e.md` to automate from Idea -> Plan -> Doing -> Done.
- **Phase 1: Research & Design** - ALWAYS use the `brainstorming` skill before any implementation.
- **Phase 2: Planning** - ALWAYS use `writing-plans` to break down tasks into small, verifiable steps.
- **Phase 3: Implementation** - STRICTLY follow `test-driven-development`. Write the test first, see it fail, then implement.
- **Phase 4: Verification** - ALWAYS use `verification-before-completion` and `requesting-code-review`.

## 🧠 Hermes Learning Loop (Self-Improvement)
1. **Extraction:** After completing any non-trivial task, the agent MUST evaluate if the logic or workflow can be generalized.
2. **Skill Creation:** If generalized, the agent MUST propose creating a new skill in `.agent/skills/[skill-name]/SKILL.md`.
3. **Knowledge Base:** Maintain a project-wide `scratchpad/knowledge_base.md` to store patterns, GitHub research findings, and architectural decisions.

## 🛠️ Global Directives
1. **Never Skip Skills:** Before responding to any prompt, evaluate if a Superpowers or project-specific skill is applicable. If so, you MUST activate it first.
2. **Subagent Usage:** For complex tasks, prefer `subagent-driven-development` or `dispatching-parallel-agents` to maintain clean context.
3. **Commit Quality:** Use the `finishing-a-development-branch` workflow to ensure high-quality commits and PRs.

## 🔗 Bridge to Canifa System
While the Canifa `.agent/AGENTS.md` provides identity and general standards, **Superpowers** provides the *active execution engine* and **Hermes patterns** provide the *persistent intelligence*.

