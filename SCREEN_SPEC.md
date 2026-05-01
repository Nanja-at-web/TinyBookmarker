# SCREEN_SPEC.md — TinyBookmarker

## Purpose

This document turns the early UI wireframe into an implementation-oriented screen specification.

It defines:
- the first screens to build
- the role of each screen
- the required UI blocks
- the primary and secondary actions
- the expected empty states
- the interaction boundaries for v1

This is intentionally practical.
It should help implementation start without drifting back into feature sprawl.

---

## Product rule for all screens

TinyBookmarker is a tiny self-hosted bookmark manager for checking, cleaning and managing bookmarks.

Every primary screen must help users do one or more of these things clearly:

- save bookmarks
- browse bookmarks
- organize bookmarks
- clean duplicates
- move bookmarks in or out safely

Screens should not feel like:
- technical dashboards
- read-later readers
- archive browsers
- admin panels with bookmark features attached

---

## Global shell

All primary product screens share the same shell:

### Topbar
Contains only:
- product name / logo
- global search
- primary action: `+ New Bookmark`
- profile/account menu

### Sidebar
Contains only the stable main areas:

#### Primary work
- All Bookmarks
- Favorites

#### Organization
- Collections
- Tags

#### Maintenance / migration
- Duplicates
- Import / Export

#### Secondary
- Profile
- Settings
- System
- Admin

### Main area
Every screen begins with:
- title
- subtitle
- primary tools
- main content
- empty state when relevant

---

# PHASE 1 IMPLEMENTATION SCOPE

The first implementation block should cover only:

1. All Bookmarks
2. Quick Add / + New Bookmark
3. Bookmark create/edit basics
4. Favorites basics
5. Collections/Tags assignment basics inside bookmark editing

Do not start with:
- duplicates
- import/export
- companion
- system/admin depth
- advanced sync logic

Those will come later.

---

# Screen 1 — All Bookmarks

## Purpose
This is the main daily workspace.

A user should be able to:
- see all bookmarks
- search bookmarks
- sort bookmarks
- filter bookmarks in a basic way
- open a bookmark
- edit a bookmark
- favorite/unfavorite a bookmark
- see basic organization state

## Title
**All Bookmarks**

## Subtitle
Your full bookmark library.  
Use this area for everyday bookmark work.

## Required UI blocks

### A. Header
- Title: `All Bookmarks`
- Subtitle text
- optional result count

### B. Main toolbar
Must include:
- search field
- sort control
- lightweight filter control
- display mode switch only if it stays simple

### C. Bookmark list
Each bookmark row/card should show:
- title
- URL/domain
- favorite state
- collection(s) if assigned
- tag(s) if assigned
- updated/saved date if useful
- open action
- edit action

### D. Selection / bulk area
Only appear when bookmarks are selected.

For the first version, keep bulk actions minimal:
- add to collection
- add tag
- favorite / unfavorite

### E. Empty state
If there are no bookmarks:
- explain what this screen is for
- point to `+ New Bookmark`
- optionally mention import, but do not let import dominate the message

## First-version filters
Keep the first set small:
- Favorites only
- Unsorted / Inbox only
- Collection
- Tag

Do not overload the first version with too many filter chips.

## First-version success criteria
A new user can land here and understand:
- this is the main bookmark workspace
- where to search
- how to add a bookmark
- how to edit/favorite/organize a bookmark

---

# Screen 2 — Quick Add / + New Bookmark

## Purpose
This is the single clear primary creation flow.

It should be the fastest path to adding a bookmark.

## Trigger
- `+ New Bookmark` button in topbar

## Title
**New Bookmark**

## Subtitle
Save a bookmark now.  
You can organize it immediately or review it later.

## Required fields

### Required
- URL

### Recommended visible by default
- Title
- Favorite toggle

### Secondary / collapsible
- Collections
- Tags
- Notes / description

## Required behavior
- sensible defaults
- keyboard-friendly
- clear submit button
- success feedback
- duplicate preflight hook point for later phases

## First-version default behavior
If the bookmark is saved without organization:
- it should still be valid
- it may be treated as inbox/unsorted state

## Empty / helper text behavior
If URL is blank:
- show short guidance
- do not over-explain

## First-version success criteria
A user can save a bookmark in seconds without being overwhelmed.

---

# Screen 3 — Bookmark Detail / Edit

## Purpose
This is where a single bookmark can be reviewed and edited clearly.

## Title
**Bookmark Details** or the bookmark title itself

## Required fields / sections
- URL
- Title
- Favorite state
- Collections
- Tags
- Notes / description
- saved / updated metadata if helpful

## Required actions
- save changes
- cancel / close
- open bookmark
- delete bookmark (only if clear and safe)

## Rules
- keep layout simple
- do not turn this into a metadata wall
- prefer clear labels over too many fields

## First-version success criteria
A user can understand and edit a bookmark without confusion.

---

# Screen 4 — Favorites

## Purpose
This is the personal quick-access area.

Favorites are a personal state, not a structure.

## Title
**Favorites**

## Subtitle
Your personal quick-access bookmarks.

## Required UI blocks
- same general list structure as All Bookmarks
- search within favorites
- sort
- quick unfavorite action

## Empty state
Explain:
- what favorites are
- how to mark bookmarks as favorites
- that favorites do not replace collections

## First-version success criteria
A user can treat favorites as a personal shortcut layer.

---

# Minimal organization support in phase 1

Collections and Tags do not need their full dedicated screens in the very first implementation block.

But bookmark creation/editing must already support:

- assigning one or more collections if the data model allows
- assigning tags
- showing current collection/tag assignments in list/detail views

That keeps the object model honest from the start.

---

# Phase 1 interaction rules

## Rule 1
One main creation flow only:
- `+ New Bookmark`

## Rule 2
All Bookmarks is the main daily workspace.

## Rule 3
Favorites is a personal layer, not a structural substitute.

## Rule 4
Collections and Tags are visible in bookmark state even before their screens are fully built.

## Rule 5
Do not let admin/system/settings complexity enter the first core workspace build.

---

# Explicitly not in first implementation block

Do not implement these before the main bookmark workspace is solid:

- duplicate review screen
- import/export flow
- browser roundtrip companion UX
- advanced bulk logic
- saved views complexity
- advanced filter systems
- archive mode
- reader mode
- heavy dashboard widgets

---

# Design rules for implementation

- prefer calm layout over dense control surfaces
- use clear titles and subtitles
- show only the most useful controls first
- keep bulk tools contextual
- avoid too many equal-weight buttons
- preserve obvious next actions
- optimize for daily bookmark work, not feature exposure

---

# Screen priority order

Build in this order:

1. Global shell (topbar + sidebar)
2. All Bookmarks
3. Quick Add / New Bookmark
4. Bookmark Detail / Edit
5. Favorites
6. Collection/Tag assignment support in create/edit/list views

Only then move to:
7. Collections screen
8. Tags screen
9. Duplicates
10. Import / Export
11. Secondary screens polish

---

# Implementation-ready checklist

Before coding starts, confirm:

- [ ] All Bookmarks is defined as the main workspace
- [ ] `+ New Bookmark` is the single primary creation flow
- [ ] Favorites is clearly defined as personal quick access
- [ ] Collections and Tags are kept distinct
- [ ] Secondary areas are not driving phase 1
- [ ] Empty states are intentional
- [ ] First-version scope is small enough to stay calm

---

# Final reminder

If the first implementation block already feels crowded,
the scope is too large.

TinyBookmarker should start with a clear bookmark workspace,
not with every possible feature visible at once.
