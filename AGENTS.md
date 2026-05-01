# AGENTS.md

Read `CLAUDE.md` first and follow it as the main project steering document for this repository.

If `CLAUDE.md`, active product docs, older notes, backup files, historical summaries, or outdated implementation details conflict, `CLAUDE.md` and the active product docs win.

## Non-negotiable project direction

- TinyBookmarker is primarily a self-hosted bookmark manager.
- It must stay focused on checking, cleaning and managing bookmarks.
- It must not drift into a read-later-first, reader-first or archive-first product.
- It should feel like a practical bookmark workspace, not a technical dashboard.

## Files to read first

Before making product, UI, UX, workflow or architecture decisions, read:

- `CLAUDE.md`
- `README.md`
- `PRODUCT_ONE_PAGER.md`
- `ROADMAP.md`
- `LESSONS_LEARNED.md`

## Product priorities

Prioritize work that strengthens:

- bookmark-centered navigation and information architecture
- quick add and everyday save flow
- favorites, collections and tags as real working surfaces
- duplicate review, safe merge and cleanup
- import/export and migration clarity
- browser roundtrip support
- lightweight self-hosting

## Working rules

- Treat the active Markdown files as the current source of truth.
- Historical notes are reference only.
- Compare actual code and UI against the active docs before making larger changes.
- Prefer small, logically separated changes.
- Avoid product drift.
- Keep wording user-facing and understandable.
- Preserve one clear primary creation flow.
- Keep secondary/system areas visible but subordinate.
- Run relevant tests after code changes.
- Leave the worktree clean.

## UI / UX guidance

Favor:

- fewer equal-weight navigation items
- clearer hierarchy
- clearer naming
- strong separation between primary and secondary actions
- visible bookmark work areas
- visible but controlled cleanup and migration areas
- calm, understandable layouts

Reference direction:
- linkding-like core simplicity
- Linkwarden-like structural clarity
- Karakeep-like organizational ambition, but only when it does not overwhelm the core

Do not copy these products directly.
Use them as references for clarity, not identity.

## Validation rule

Before finishing a task, ask:

- Does this make TinyBookmarker better at checking, cleaning and managing bookmarks?
- Or does it mainly make it more like a reader, archive system, technical dashboard, or unfocused multi-tool?

If the second is true, the direction is likely wrong.
