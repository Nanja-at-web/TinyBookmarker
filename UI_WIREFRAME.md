# UI_WIREFRAME.md — TinyBookmarker

## Purpose

This document defines the first UI structure for TinyBookmarker before deeper implementation begins.

It is intentionally simple.
The goal is not visual polish yet.
The goal is to lock the product structure early so the UI does not drift into the same confusion as the earlier project.

TinyBookmarker should feel like:

- a calm bookmark workspace
- a practical self-hosted tool
- a product with one clear main workflow
- a product where primary work and secondary/system areas are clearly separated

It should not feel like:

- a technical dashboard
- a read-later reader
- an archive-first control panel
- a collection of unrelated tabs

---

## Core layout model

TinyBookmarker should use a stable three-part layout:

1. **Topbar**
2. **Sidebar**
3. **Main content area**

This layout should remain consistent across the primary product areas.

---

## Topbar

The topbar should contain only the most global, high-value actions.

### Topbar contents
- product name / logo
- global search
- primary action: `+ New Bookmark`
- profile / account menu

### Topbar rules
- keep it visually light
- do not overload it with secondary actions
- the primary action must always remain obvious
- search should feel central, not hidden

### Example
```text
[ TinyBookmarker ] [ Search bookmarks........................ ] [+ New Bookmark] [ Profile ]
```

---

## Sidebar

The sidebar should provide the primary structure of the product.

It should separate:

- daily bookmark work
- structural organization
- maintenance / migration
- secondary/system areas

### Sidebar groups

#### Primary work
- All Bookmarks
- Favorites

#### Organization
- Collections
- Tags

#### Maintenance and migration
- Duplicates
- Import / Export

#### Secondary
- Profile
- Settings
- System
- Admin

### Sidebar rules
- primary work appears first
- secondary/system areas appear last
- do not let secondary areas compete visually with bookmark work
- use consistent labels
- avoid too many equal-weight items
- sidebar labels should be short and obvious

### Example
```text
PRIMARY
- All Bookmarks
- Favorites

ORGANIZATION
- Collections
- Tags

MAINTENANCE
- Duplicates
- Import / Export

SECONDARY
- Profile
- Settings
- System
- Admin
```

---

## Main content area

The main content area should always answer three questions quickly:

1. Where am I?
2. What is this area for?
3. What should I do next?

Each main screen should therefore start with:

- a clear title
- a short subtitle / helper line
- the main actions relevant for that screen
- the content itself

### Structure pattern
```text
[ Screen Title ]
[ Short explanation of what this area is for ]

[ Primary actions / filters / tools for this area ]

[ Main content ]
```

---

# Main screens

## 1. All Bookmarks

### Purpose
This is the main daily workspace.

It should be the place where users:
- browse their full bookmark library
- search
- filter
- sort
- bulk-select
- open detail/edit views

### Title
**All Bookmarks**

### Subtitle
Your full bookmark library.  
Use this area for everyday bookmark work.

### Main tools
- search
- sort
- filters
- display mode
- bulk selection actions

### Empty state
When there are no bookmarks yet:
- explain what this area is
- point to `+ New Bookmark`
- optionally mention import

### Rules
- this screen must stay calm
- do not let all controls compete equally
- filters should help, not dominate
- bulk actions should only become prominent when selection is active

---

## 2. Favorites

### Purpose
This is the personal quick-access area.

Favorites are not structural containers.
They mark importance.

### Title
**Favorites**

### Subtitle
Your personal quick-access bookmarks.  
Favorites help you surface important items quickly.

### Main tools
- search within favorites
- sort
- bulk favorite removal if needed

### Empty state
Explain:
- what favorites are
- how to mark bookmarks as favorites
- that favorites do not replace collections

---

## 3. Collections

### Purpose
Collections are structural groups for bookmarks.

They should feel like real objects, not just filters.

### Title
**Collections**

### Subtitle
Use collections to group bookmarks into clear structural areas.

### Main tools
- create collection
- rename collection
- delete collection
- open collection
- assign bookmarks to collections

### Empty state
Explain:
- that collections are for structure
- that tags are different and more flexible
- how to create the first collection

---

## 4. Tags

### Purpose
Tags are flexible labels that work across collections.

They should feel lighter and more cross-cutting than collections.

### Title
**Tags**

### Subtitle
Use tags as flexible labels across topics, collections and workflows.

### Main tools
- create tag
- rename tag
- delete tag
- filter by tag
- assign bookmarks to tags

### Empty state
Explain:
- that tags are flexible labels
- that collections are structural groups
- how to create the first tag

---

## 5. Duplicates

### Purpose
This is the maintenance area for duplicate review and cleanup.

It should feel safe and review-oriented, not destructive.

### Title
**Duplicates**

### Subtitle
Review and clean up possible duplicate bookmarks safely.

### Main tools
- review duplicate groups
- dry-run
- merge
- skip
- undo / recent merge history

### Empty state
Explain:
- that this area is for duplicate maintenance
- that no blind deletion happens
- that duplicates can be reviewed before changes are applied

---

## 6. Import / Export

### Purpose
This is the migration area.

It should not feel like the normal save flow.
It should clearly communicate that it is for moving bookmark data in and out.

### Title
**Import / Export**

### Subtitle
Use this area for migration, browser import/export and roundtrip workflows.

### Main tools
- choose format
- choose file
- preview import
- run import
- export bookmarks
- review recent import/export sessions

### Empty state
Explain:
- that this area is for migration, not daily saving
- that preview comes before apply
- that exports can be used for backup or browser transfer

---

# Secondary screens

## 7. Profile

### Purpose
Personal account area.

### Title
**Profile**

### Subtitle
Manage your personal account details and API-related identity settings.

### Rules
- keep concise
- avoid system/admin language here

---

## 8. Settings

### Purpose
Personal preferences, not system operations.

### Title
**Settings**

### Subtitle
Adjust personal display and behavior preferences.

### Rules
- do not turn this into a generic redirect page
- keep it clearly separate from system/admin work

---

## 9. System

### Purpose
Operational self-host area.

### Title
**System**

### Subtitle
View health, version, backup and update information for your self-hosted setup.

### Rules
- system belongs here, not in the bookmark workspace
- operational info should be clear but secondary

---

## 10. Admin

### Purpose
Administrative area for user and system-level management.

### Title
**Admin**

### Subtitle
Manage users and administrative controls.

### Rules
- visible only where appropriate
- clearly separate from normal user workflow

---

# Primary workflow

TinyBookmarker should reinforce one clear primary workflow:

1. add a bookmark
2. optionally land in Inbox / triage
3. organize with favorites, collections and tags
4. return later through bookmarks/search/favorites
5. clean duplicates when needed
6. import/export only when migrating

This flow should remain more prominent than:
- system tasks
- admin tasks
- advanced migration tasks

---

# UI hierarchy rules

## Primary should feel primary
These should always feel strongest:
- All Bookmarks
- Favorites
- + New Bookmark
- search

## Structural organization should feel supportive
- Collections
- Tags

## Maintenance should feel important but not dominant
- Duplicates
- Import / Export

## Secondary should feel secondary
- Profile
- Settings
- System
- Admin

---

# Naming rules

Use words that are:
- short
- user-facing
- obvious
- stable across screens

Prefer:
- All Bookmarks
- Favorites
- Collections
- Tags
- Duplicates
- Import / Export
- Profile
- Settings
- System
- Admin

Avoid:
- overly technical labels
- internal architecture terms
- feature-heavy titles
- ambiguous synonyms that blur the product model

---

# Empty state rules

Every empty state should answer:

1. What is this area for?
2. Why is it empty?
3. What should the user do next?

Avoid passive empty states like:
- “Nothing here yet.”

Prefer:
- a short explanation
- one clear next step
- one relevant action

---

# Anti-drift rules

This UI structure exists to prevent the product from drifting into:

- a read-later UI
- an archive-first UI
- a system dashboard
- a feature soup
- a tab overload interface

If a future UI change makes the product harder to explain in one sentence, the change should be questioned.

---

# Decision test

Before implementing a UI change, ask:

- Does this make the main bookmark workspace clearer?
- Does it preserve the distinction between bookmarks, favorites, collections, tags, duplicates and migration?
- Does it keep system/admin areas secondary?
- Does it help the product feel calm, useful and lightweight?

If not, the change is probably wrong or too early.
