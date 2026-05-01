# LESSONS_LEARNED.md — TinyBookmarker

## Purpose

This file captures the main mistakes and anti-patterns that should not be repeated in TinyBookmarker.

It is intentionally separate from the core product files.

The goal is to preserve lessons without polluting the README, product one-pager, roadmap, or agent steering files.

## What went wrong in the earlier project

### 1. Product identity drift
The earlier project gradually mixed together too many identities:

- bookmark manager
- favorites tool
- duplicate cleanup tool
- import/export utility
- browser sync helper
- archive/read-later direction
- system dashboard
- admin/control panel

Result:
the product became harder to explain and harder to feel.

### 2. Too much was defined after implementation
Features and structures were often implemented first, then explained afterward.

Result:
the product model became reactive instead of intentional.

### 3. UI and IA were treated too late
Navigation, naming, area logic, empty states, panel titles and microcopy were improved late.

Result:
the product stayed technically stronger than it felt.

### 4. Too many equal-weight areas
Daily bookmark work, cleanup flows, migration, system functions and administrative areas competed too equally for attention.

Result:
the UI felt like a control surface instead of a calm bookmark workspace.

### 5. Concepts blurred together
Important concepts were not always clearly separated:

- inbox vs bookmarks
- tags vs collections
- favorites vs structure
- duplicates vs general cleanup
- import/export vs everyday save flow
- profile/settings/system/admin

Result:
users had to infer product meaning from implementation details.

### 6. Too much patching, not enough reset
Instead of stopping and redefining the product clearly, too many small fixes accumulated.

Result:
effort increased faster than clarity.

### 7. Name problems were discovered too late
A product name was used too long before checking broader collisions and product fit.

Result:
identity work and implementation drift were tied to a weak name foundation.

## Rules for TinyBookmarker

### Rule 1
Define the product in one sentence first.

### Rule 2
Define non-goals early and keep them visible.

### Rule 3
Keep the product model small and stable.

### Rule 4
Do not mix primary bookmark work with secondary system/admin areas.

### Rule 5
Do not grow features faster than clarity.

### Rule 6
Do not let migration, duplicate handling or system tooling become the whole product identity.

### Rule 7
Do not treat UI/IA clarity as “later polish”.

### Rule 8
When the product starts to feel confusing, stop and simplify instead of patching endlessly.

## What TinyBookmarker should preserve

Even though the earlier project drifted in some ways, these lessons were still valuable:

- duplicate handling can be a real differentiator
- import/export and browser roundtrip support create strong product value
- self-hosting quality matters
- favorites need to be first-class
- collections and tags must be clearly distinct
- one strong primary creation flow is better than competing entry points

## Final reminder

TinyBookmarker should stay small, clear and intentional.

If a change makes the product harder to explain in one sentence, that is a warning sign.
