# 01 — FireStation UI/UX Overhaul Epic

> Ported from: `plan/ideas/01_ui_ux_overhaul.md`
> Started: 2026-05-01

## Phase 1: Fireplexity-style Search Results Layout
- [x] 1.1 Rebuild `style.css` with progressive animation system (fade-up, slide-in, stagger delays)
- [x] 1.2 Rebuild `app.js` with section-based SSE rendering (Sources → Answer → Related)
- [x] 1.3 Add labeled section headers with icons (📄 Sources, ✨ Answer, 💡 Related)
- [x] 1.4 Implement 5-column source cards with favicon, title, domain, character counter
- [x] 1.5 Add copy/rewrite buttons on Answer section
- [x] 1.6 Add "Deep Research" mode badge as prominent header (not corner)

## Phase 2: Deep Research Progress Panel
- [x] 2.1 Add thinking steps sidebar (firesearch-style) for Deep mode
- [x] 2.2 Add timer + source counter in progress header
- [x] 2.3 Add animated thinking line with favicon rotation
- [x] 2.4 Phase tracker: Understanding → Planning → Searching → Analyzing → Synthesizing → Complete

## Phase 3: Architecture Documentation Page
- [x] 3.1 Create `docs.html` with Mermaid diagrams showing Quick Search flow
- [x] 3.2 Add Deep Research flow diagram
- [x] 3.3 Add SSE event lifecycle diagram
- [x] 3.4 Add component interaction diagram

## Phase 4: Visual Testing & Polish
- [x] 4.1 Browser test empty state
- [x] 4.2 Browser test Quick Search flow (SSE streaming)
- [x] 4.3 Browser test Deep Research mode toggle
- [x] 4.4 Browser test responsive layout
