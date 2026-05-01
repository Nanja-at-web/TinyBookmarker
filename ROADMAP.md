# ROADMAP.md — TinyBookmarker

## Product direction

TinyBookmarker is a tiny self-hosted bookmark manager for checking, cleaning and managing bookmarks.

The product is primarily about:

- saving bookmarks quickly
- managing favorites
- organizing bookmarks clearly
- searching, filtering and sorting effectively
- reviewing and cleaning up duplicates safely
- importing and exporting bookmark data reliably
- staying lightweight and practical for self-hosting

TinyBookmarker is **not primarily**:

- a read-later app
- a reader-first product
- an archive-first product
- a knowledge-base-first tool
- a note-taking-first product
- a technical dashboard

## Guiding principles

### 1. Bookmark-first
Every major decision should improve the core bookmark workflow.

### 2. Calm workspace
The UI should feel clear, structured and low-friction.

### 3. Safe by default
Duplicate handling, import/export and roundtrip flows must be understandable and reviewable.

### 4. Lightweight by default
The standard self-hosted path should stay small, practical and easy to maintain.

### 5. Migration matters
Import/export and browser roundtrip support are core product value, not side features.

## Core product model

- Bookmark = main object
- Favorite = personal prominence / quick access
- Collection = structural grouping
- Tag = flexible label
- Duplicate = maintenance / cleanup area
- Import / Export = migration area
- Profile / Settings / System / Admin = secondary areas

## Version 1 goal

Version 1 should already feel like a coherent bookmark product, not a prototype.

A user should be able to:

- add bookmarks quickly
- browse and search bookmarks
- mark favorites
- organize bookmarks with collections and tags
- review duplicates safely
- import/export bookmark data
- use a basic browser roundtrip flow
- run the system easily in a lightweight self-host setup

## Phase 0 — Product foundation

### Goal
Define the product before growing it.

### Deliverables
- final product sentence
- non-goals
- stable object model
- README
- CLAUDE.md
- AGENTS.md
- one-pager
- roadmap
- initial wireframe / screen structure

### Done when
- the product can be explained clearly in one sentence
- main concepts do not blur together
- early UI structure is agreed before major implementation

## Phase 1 — Core bookmark workspace

### Goal
Make the daily bookmark area feel complete and clear.

### Included
- All Bookmarks
- Quick Add / + New Bookmark
- search
- filter
- sorting
- list/grid display
- bookmark detail / edit
- empty states
- clear primary and secondary actions

### Done when
- users can immediately understand where daily bookmark work happens
- the main workspace feels focused, not cluttered

## Phase 2 — Favorites, collections and tags

### Goal
Turn organization into real working surfaces.

### Included
- Favorites view
- collection view
- tag view
- create / rename / delete collections
- create / rename / delete tags
- assign / unassign bookmarks
- bulk actions

### Done when
- users can organize bookmarks without guessing what each concept means

## Phase 3 — Duplicate review and cleanup

### Goal
Make duplicate handling a first-class product strength.

### Included
- duplicate preflight on save
- duplicate review area
- exact and normalized match handling
- dry-run
- safe merge
- undo / history
- review-oriented microcopy

### Done when
- users can clean up duplicates with confidence

## Phase 4 — Import / export / migration

### Goal
Make migration a strong reason to use the product.

### Included
- HTML import
- browser-aware import paths
- export
- preview before apply
- result summary
- provenance / source visibility
- migration-friendly empty states and guidance

### Done when
- a user can move bookmarks in or out without confusion

## Phase 5 — Browser roundtrip basics

### Goal
Support practical browser-to-server and server-to-browser workflows.

### Included
- companion basics
- save current tab
- browser bookmark preview
- restore preview
- safe apply flow
- conflict/duplicate visibility
- connection status

### Done when
- the browser companion feels like a practical extension of the bookmark product

## Phase 6 — Self-hosting quality

### Goal
Make the product practical to deploy, update and maintain.

### Included
- install flow
- update flow
- helper scripts
- health/version/build visibility
- backup/restore basics
- Proxmox-friendly path
- documentation for self-hosting

### Done when
- installation and updates are routine, not fragile

## Phase 7 — Product polish

### Goal
Tighten clarity, consistency and trust.

### Included
- naming review
- empty state review
- panel title review
- microcopy refinement
- visual hierarchy refinement
- consistency across screens
- version/build consistency
- final cleanup of rough edges

### Done when
- the product feels coherent and intentionally designed

## Explicitly later / optional

These may be explored later, but should not drive the early product:

- reader mode
- archive-first workflows
- AI-heavy features
- screenshots/PDF as a core product axis
- team-first collaboration
- enterprise provisioning
- heavy service architecture

## Success criteria

TinyBookmarker is succeeding when:

- the daily bookmark workflow is obvious
- the product feels calm and structured
- organization is useful and clear
- duplicates are safe to review
- migration is trustworthy
- self-hosting is practical
- the product does not feel like a dashboard or a reader app

## Decision rule

Before any major feature or UI change, ask:

**Does this make TinyBookmarker better at checking, cleaning and managing bookmarks?**

If not, it is probably too early or the wrong direction.
