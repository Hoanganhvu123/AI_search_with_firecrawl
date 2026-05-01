# 01 — FireStation UI/UX Overhaul + Feature Architecture

## Idea Summary
Rebuild the FireStation search UI to match the UX quality of the 3 reference codebases (fireplexity, firesearch, preference), with:
1. **Progressive SSE rendering** — Each event type (status, sources, answer chunks, follow-ups) animates in sequentially like firesearch/fireplexity
2. **Deep Research mode** — Port the LangGraph multi-step research from firesearch (search-display.tsx: thinking steps sidebar, progress tracker, source processing pipeline)
3. **Fireplexity-style source cards** — 5-column grid with favicon, title, character counter, hover effects
4. **Answer section headers** — Labeled sections ("Sources", "Answer", "Related") with icons, copy/rewrite buttons
5. **Architecture docs page** — Standalone HTML page with Mermaid diagrams showing both feature flows

## Reference Files Analyzed
| Feature | Source File | Key Patterns |
|---|---|---|
| Chat UI + Source Cards | `fireplexity/app/chat-interface.tsx` | 5-col grid, image bg, character counter, animate-fade-up |
| Deep Research Progress | `preference/firesearch/app/search-display.tsx` | Step sidebar, phase tracker, source processing states, timer |
| SSE Event Types | `preference/firesearch/lib/langgraph-search-engine.ts` | thinking, searching, found, source-processing, content-chunk, final-result |
| Markdown Rendering | `fireplexity/app/markdown-renderer.tsx` | Citation tooltips, inline source refs |
| Search Display Layout | `preference/firesearch/app/search-display.tsx` | Split view: steps sidebar (w=56) + main content |

## UX Issues to Fix
1. Mode badge ("Deep Research") shows at bottom-right corner — should be prominent at top
2. SSE events render all at once — should animate in progressively (fade-up with staggered delay)
3. Source cards are too small/plain — need fireplexity-style 5-column rich cards
4. No section headers — need "Sources", "Answer", "Related" labels with icons
5. No progress indicator for Deep Research — need firesearch-style thinking steps sidebar
6. No copy/rewrite buttons on answers
7. No character counter on source cards
8. No timer showing research elapsed time

## Priority
**HIGH** — Core UX quality directly impacts user trust and engagement

## Classification
**Pipeline A: Standard Feature** (existing project, new features)
