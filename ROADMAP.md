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

---

## Phase 0 — Product foundation ✅ DONE

### Goal
Define the product before growing it.

### Completed
- Final product sentence
- Non-goals defined
- Stable object model (schema.sql: bookmarks, collections, tags, bookmark_collections, bookmark_tags)
- README, CLAUDE.md, AGENTS.md
- PRODUCT_ONE_PAGER.md, ROADMAP.md
- UI_WIREFRAME.md, SCREEN_SPEC.md, LESSONS_LEARNED.md

---

## Phase 1 — Core bookmark workspace ✅ ~DONE

### Goal
Make the daily bookmark area feel complete and clear.

### Completed
- All Bookmarks (route, toolbar, list, empty states)
- Quick Add / + New Bookmark (form, URL prefill via `?url=`)
- Search (full-text: title, URL, description, collection name, tag name)
- Filter (unsorted, collection, tag)
- Sorting (newest / oldest / title)
- Bookmark detail / edit / delete / toggle-favorite
- Empty states (real-empty vs. no-results, distinct copy)
- Favorites view (dedicated route, own empty states)
- Duplicate preflight on save (exact URL match, link to existing)
- Dark mode (`prefers-color-scheme: dark`, manual theme toggle)
- Responsive layout (basic sidebar collapse)

### Optional — low priority, does not block Phase 2
- TASK-101: Grid display
  - Grid-view as alternative to list-view
  - Priority: low · Complexity: medium
  - Recommendation: defer to Phase 7

### Done when
- ✅ Users can immediately understand where daily bookmark work happens
- ✅ The main workspace feels focused, not cluttered

---

## Phase 2 — Favorites, collections and tags 🔄 IN PROGRESS

### Goal
Turn organization into real working surfaces.

### Completed
- Favorites view (dedicated `/favorites` route)
- Inline collection create in bookmark form (`new_collections` field, `get_or_create_collection()`)
- Inline tag create in bookmark form (`tags` field, `get_or_create_tag()`)
- Collection and tag assignment / removal in bookmark edit form

### Open tasks

- TASK-201: Collections screen
  - Routes: `GET /collections`, `POST /collections/new`, `POST /collections/<id>/rename`, `POST /collections/<id>/delete`
  - Show bookmark count per collection
  - Sidebar link "Collections" active (remove `sidebar-soon` stub)
  - Acceptance criteria: full CRUD works; sidebar link active with correct active-state
  - Priority: **critical** · Complexity: medium · Dependencies: none (data layer already complete)

- TASK-202: Tags screen
  - Routes: `GET /tags`, `POST /tags/<id>/rename`, `POST /tags/<id>/delete`
  - Show bookmark count per tag
  - Sidebar link "Tags" active
  - Acceptance criteria: full CRUD works; sidebar link active
  - Priority: **high** · Complexity: medium · Dependencies: after TASK-201

- TASK-203: Bulk actions
  - Checkbox selection in bookmark rows
  - Bulk: add to collection, add tag, favorite / unfavorite
  - Acceptance criteria: multi-select works; at least 3 bulk operations
  - Priority: medium · Complexity: high · Dependencies: TASK-201 + TASK-202

### Done when
- Users can manage collections and tags without going through a bookmark form

---

## Phase 3 — Duplicate review and cleanup 🔄 PARTIAL

### Goal
Make duplicate handling a first-class product strength.

### Completed
- Duplicate preflight on save (exact URL match, blocks save, shows link to existing)

### Open tasks

- TASK-301: URL normalisation
  - `normalize_url()` function in `bookmarks.py`
  - Handles: http/https, trailing slash, `www.` prefix, common query-param variants
  - Acceptance criteria: normalised variants are detected as duplicates
  - Priority: medium · Complexity: medium · Dependencies: none

- TASK-302: Duplicate review area
  - Route `GET /duplicates` — show duplicate groups (exact URL match to start)
  - keep / discard UX with confirmation before any delete
  - Sidebar link "Duplicates" active
  - Acceptance criteria: groups visible; safe delete with confirmation; empty state explained
  - Priority: **high** · Complexity: high · Dependencies: Phase 2 stable

- TASK-303: Dry-run, safe merge, undo / history
  - Dry-run previews what would be deleted
  - Safe merge preserves chosen bookmark's metadata
  - Undo for last action
  - Acceptance criteria: no blind bulk delete possible
  - Priority: medium · Complexity: high · Dependencies: TASK-302

### Done when
- Users can clean up duplicates with confidence

---

## Phase 4 — Import / export / migration ⬜ OPEN

### Goal
Make migration a strong reason to use the product.

### Technical prerequisite
- TASK-TECH-01: Pagination in `list_bookmarks()` — necessary before import can load large libraries

### Tasks

- TASK-401: HTML import (Netscape / browser export format)
  - File upload, parse, preview-before-apply, duplicate handling during import, result summary
  - Acceptance criteria: imports a standard browser HTML export without data loss
  - Priority: medium · Complexity: medium-high

- TASK-402: Export (HTML + JSON)
  - All bookmarks exportable; collections and tags preserved
  - Acceptance criteria: exported file re-importable without data loss
  - Priority: medium · Complexity: low-medium · Dependencies: after TASK-401

- TASK-403: Provenance / source visibility
  - Show import source on bookmarks
  - Priority: low · Dependencies: TASK-401

### Done when
- A user can move bookmarks in or out without confusion

---

## Phase 5 — Browser roundtrip basics ⬜ OPEN

### Goal
Support practical browser-to-server and server-to-browser workflows.

### Prerequisite
- TASK-500: Companion design document
  - Technology decision: browser extension vs. bookmarklet vs. API-only
  - Must be written before implementation starts

### Tasks (after design decision)
- TASK-501: Save current tab
- TASK-502: Browser bookmark preview
- TASK-503: Restore preview and safe apply flow
- TASK-504: Conflict / duplicate visibility in roundtrip
- TASK-505: Connection status

### Done when
- The browser companion feels like a practical extension of the bookmark product

---

## Phase 6 — Self-hosting quality ⬜ OPEN

### Goal
Make the product practical to deploy, update and maintain.

### Tasks

- TASK-601: Docker setup + basic documentation
  - Dockerfile, docker-compose.yml, install instructions in README
  - Priority: medium · Complexity: medium

- TASK-602: Health / version route (`GET /health`)
  - Returns version, uptime, db status
  - Priority: low · Complexity: low

- TASK-603: Backup / restore documentation
  - Priority: low · Complexity: low

- TASK-604: Proxmox-friendly install path
  - Priority: low · Complexity: medium

### Done when
- Installation and updates are routine, not fragile

---

## Phase 7 — Product polish ⬜ ONGOING

### Goal
Tighten clarity, consistency and trust.

### Approach
Revisit after each major phase (Phase 2, 3, 4) is complete.

### Areas
- Naming review across all screens
- Empty state review for new screens
- Panel title and subtitle review
- Microcopy refinement
- Visual hierarchy consistency
- Version / build consistency
- Final cleanup of rough edges

### Also deferred here
- TASK-101: Grid display (optional)

### Done when
- The product feels coherent and intentionally designed

---

## Technical debt (tracked separately from phases)

These are not features — they are quality and safety improvements.
Address before or alongside the phases indicated.

| Task | Description | Before | Priority |
|---|---|---|---|
| TASK-TECH-01 | Pagination in `list_bookmarks()` — LIMIT/OFFSET | Phase 4 | medium |
| TASK-TECH-02 | CSRF protection (Flask-WTF or manual token) | Phase 6 | medium-high |
| TASK-TECH-03 | Auth scope decision documented (no-auth vs. HTTP Basic) | Phase 2 complete | high (if public) |
| TASK-TECH-04 | URL normalisation — see also TASK-301 | Phase 3 | medium |
| TASK-TECH-05 | WAL mode in `db.py _connect()` | Phase 4 | low-medium |
| TASK-TECH-06 | Error templates (404.html, 500.html) | Phase 7 | low |
| TASK-TECH-07 | Pin requirements.txt; add requirements-dev.txt with pytest | Phase 6 | low |

---

## Explicitly later / optional

These may be explored later, but should not drive the early product:

- reader mode
- archive-first workflows
- AI-heavy features
- screenshots / PDF as a core product axis
- team-first collaboration
- enterprise provisioning
- heavy service architecture

---

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
