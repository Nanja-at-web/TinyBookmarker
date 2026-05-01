# CLAUDE.md — TinyBookmarker

> Operational project context for Claude Code and other coding assistants.

## Project overview

**TinyBookmarker** is a tiny self-hosted bookmark manager.

### Product sentence
TinyBookmarker helps users check, clean and manage their bookmarks.

## Non-negotiable product direction

TinyBookmarker is primarily:

- a bookmark manager
- a favorites manager
- a link organization tool
- a duplicate cleanup tool
- an import/export and browser-roundtrip product

TinyBookmarker is **not primarily**:

- a read-later app
- a reader-first product
- an archive-first product
- a note-taking-first tool
- a knowledge-base-first tool
- a technical dashboard

If older notes, experiments or implementation details conflict with this direction, the product direction wins.

## Product model to preserve

These concepts must stay distinct:

- **Bookmark** = main object
- **Favorite** = personal prominence / quick access
- **Collection** = structural grouping
- **Tag** = flexible label
- **Duplicate** = maintenance / cleanup area
- **Import / Export** = migration area
- **Profile / Settings / System / Admin** = secondary areas

Do not blur these concepts without a strong reason.

## Core product pillars

### 1. Bookmark-first usability
The main daily action is saving and managing bookmarks.

### 2. Favorites-first practicality
Favorites must be visible, fast and useful.

### 3. Clear organization
Collections and tags must be understandable and easy to use.

### 4. Duplicate handling is core
Duplicate review, merge and cleanup are not side features.

### 5. Migration matters
Import/export and browser roundtrip flows are core product value.

### 6. Lightweight self-hosting
Default deployment must remain practical and low-friction.

## UI / UX direction

TinyBookmarker should feel like:

- a calm bookmark workspace
- clear in structure
- fast in daily use
- visually restrained
- user-facing, not system-facing

Favor:

- fewer equal-weight navigation items
- one strong primary creation flow
- clear separation of primary and secondary actions
- visible bookmark work areas
- visible but not dominant cleanup and migration areas
- calm layouts over feature clutter

Do not let the UI drift toward:

- technical control panel
- archive browser
- reader app
- feature soup

## Current priorities

At the start of each work session, prefer improvements in this order:

1. bookmark-centered navigation and information architecture
2. quick add and everyday save flow
3. favorites / collections / tags as real working surfaces
4. duplicate review and safe cleanup UX
5. import/export and migration UX
6. browser roundtrip clarity
7. lightweight self-hosting quality

## Scope control

These are not forbidden forever, but are **not early priorities**:

- archive-first features
- article reader mode
- AI-heavy workflows
- large collaboration / team features
- enterprise provisioning
- heavy architecture expansion

## Working rules

- Treat product clarity as a core requirement, not cosmetic polish.
- Prefer small, logically separated changes.
- Avoid internal or technical wording when a simpler user-facing term works.
- Keep the main bookmark workflow obvious.
- Keep secondary/system areas available but subordinate.
- Preserve safe-by-default behavior in duplicate and migration flows.
- Run relevant tests after changes.
- Leave the worktree clean.

## Validation rule

Before finishing a task, ask:

**Does this change make TinyBookmarker better at checking, cleaning and managing bookmarks?**

If the answer is mostly:
- “it makes it more like a reader”
- “it makes it more like an archive platform”
- “it makes it more like a technical dashboard”
- “it adds complexity without making bookmark work clearer”

then the direction is probably wrong.
