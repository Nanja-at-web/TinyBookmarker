def test_root_redirects_to_all_bookmarks(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/bookmarks")


def test_all_bookmarks_empty_state(client):
    resp = client.get("/bookmarks")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "All Bookmarks" in body
    assert "Your bookmark library is empty" in body
    assert "+ New Bookmark" in body


def test_favorites_empty_state_distinct(client):
    resp = client.get("/favorites")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Favorites" in body
    assert "No favorites yet" in body
    # Empty state must explain favorites are personal, not structural
    assert "do not replace collections" in body


def test_topbar_and_sidebar_present(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    assert "TinyBookmarker" in body
    assert "+ New Bookmark" in body
    # Sidebar groups
    assert "All Bookmarks" in body
    assert "Favorites" in body
    assert "Collections" in body
    assert "Tags" in body
    assert "Duplicates" in body
    assert "Import / Export" in body


def test_new_bookmark_form_renders(client):
    resp = client.get("/bookmarks/new")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "New Bookmark" in body
    assert "URL" in body


def test_create_bookmark_minimum_fields(client):
    resp = client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/a"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "https://example.com/a" in body or "example.com/a" in body
    assert "Bookmark saved" in body


def test_create_bookmark_rejects_missing_url(client):
    resp = client.post("/bookmarks/new", data={"url": ""})
    assert resp.status_code == 400
    assert "URL is required" in resp.get_data(as_text=True)


def test_create_bookmark_rejects_bad_scheme(client):
    resp = client.post("/bookmarks/new", data={"url": "javascript:alert(1)"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "http://" in body and "https://" in body


def test_create_bookmark_with_full_fields(client):
    resp = client.post(
        "/bookmarks/new",
        data={
            "url": "https://example.com/page",
            "title": "Example Page",
            "description": "A page",
            "is_favorite": "on",
            "tags": "news, reading",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Example Page" in body
    assert "#news" in body
    assert "#reading" in body
    # Favorite star (filled)
    assert "★" in body


def test_favorite_appears_in_favorites_view(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/x", "title": "Faved Bookmark", "is_favorite": "on"},
    )
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/y", "title": "Plain Bookmark"},
    )

    fav_body = client.get("/favorites").get_data(as_text=True)
    assert "Faved Bookmark" in fav_body
    assert "Plain Bookmark" not in fav_body


def test_toggle_favorite(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/p", "title": "Toggle Target"},
    )
    resp = client.post("/bookmarks/1/toggle-favorite", data={"next": "/favorites"})
    assert resp.status_code == 302
    assert "Toggle Target" in client.get("/favorites").get_data(as_text=True)

    client.post("/bookmarks/1/toggle-favorite", data={"next": "/favorites"})
    fav_body = client.get("/favorites").get_data(as_text=True)
    assert "Toggle Target" not in fav_body


def test_edit_bookmark_updates(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/old", "title": "Original Title"},
    )
    resp = client.post(
        "/bookmarks/1/edit",
        data={
            "url": "https://example.com/new",
            "title": "Updated Title",
            "tags": "alpha",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Updated Title" in body
    assert "Original Title" not in body
    assert "#alpha" in body


def test_delete_bookmark(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/d", "title": "Delete me"})
    resp = client.post("/bookmarks/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Delete me" not in body
    assert "Bookmark deleted" in body


def test_search_filters_list(client):
    client.post("/bookmarks/new", data={"url": "https://a.example.com/", "title": "Apple"})
    client.post("/bookmarks/new", data={"url": "https://b.example.com/", "title": "Banana"})

    resp = client.get("/bookmarks?q=Apple")
    body = resp.get_data(as_text=True)
    assert "Apple" in body
    assert "Banana" not in body


def test_unsorted_filter_shows_only_unsorted(client):
    client.post("/bookmarks/new", data={"url": "https://x.example.com/", "title": "Has Tag", "tags": "t1"})
    client.post("/bookmarks/new", data={"url": "https://y.example.com/", "title": "Just Saved"})

    resp = client.get("/bookmarks?filter=unsorted")
    body = resp.get_data(as_text=True)
    assert "Just Saved" in body
    assert "Has Tag" not in body


def test_unsorted_filter_dropdown_uses_unsorted_value(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # The dropdown option must use the user-facing param value 'unsorted'.
    assert 'value="unsorted"' in body
    # The dropdown label must explain the criterion right there.
    assert "no collection or tag" in body
    # The legacy 'inbox' value must NOT leak into the UI.
    assert 'value="inbox"' not in body


def test_unsorted_filter_active_shows_contextual_hint(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/u", "title": "Pending"})
    body = client.get("/bookmarks?filter=unsorted").get_data(as_text=True)
    # Hint visible above the list, explaining how to leave the state.
    assert "no collection or tag yet" in body
    assert "add a collection or tag" in body
    # The hint must NOT appear without the filter.
    plain = client.get("/bookmarks").get_data(as_text=True)
    assert "no collection or tag yet" not in plain


def test_toolbar_has_two_tiers_primary_and_refine(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # Primary tier wraps search + count; refine tier wraps the selects.
    assert 'class="toolbar-primary"' in body
    assert 'class="toolbar-refine"' in body
    # The toolbar tiers appear in order: primary, then refine.
    primary_index = body.index('class="toolbar-primary"')
    refine_index = body.index('class="toolbar-refine"')
    assert primary_index < refine_index
    # The refine tier must contain at least one select (name="sort" is always present).
    refine_block = body[refine_index:]
    assert 'name="sort"' in refine_block


def test_toolbar_dropdowns_apply_immediately_on_change(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # Every refine select auto-submits — no explicit Apply needed in the JS path.
    assert body.count('onchange="this.form.submit()"') >= 2  # filter + sort always present
    # The Apply button only exists as a <noscript> fallback.
    assert "<noscript>" in body
    # And it must NOT appear outside the noscript tag.
    pre_noscript = body.split("<noscript>")[0]
    assert ">Apply<" not in pre_noscript


def test_unsorted_filter_zero_state_is_friendly_success(client):
    # Every bookmark is organized via a tag.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/o", "title": "Organized", "tags": "topic"},
    )
    body = client.get("/bookmarks?filter=unsorted").get_data(as_text=True)
    # Friendly success copy, not the generic no-results copy.
    assert "Nothing is unsorted" in body
    assert "Show all bookmarks" in body
    # The generic "no matches" copy must NOT appear in this case.
    assert "No bookmarks match this view" not in body
    # And the first-run empty state must NOT appear either.
    assert "Your bookmark library is empty" not in body


def test_404_on_unknown_bookmark(client):
    assert client.get("/bookmarks/999/edit").status_code == 404
    assert client.post("/bookmarks/999/delete").status_code == 404
    assert client.post("/bookmarks/999/toggle-favorite").status_code == 404


def test_new_form_offers_first_collection_creation_when_none_exist(client):
    body = client.get("/bookmarks/new").get_data(as_text=True)
    assert 'name="new_collections"' in body
    assert "Type a name to create your first collection" in body
    # The dead "Collections area" hint must be gone.
    assert "Collections area" not in body


def test_create_bookmark_creates_first_collection_inline(client):
    resp = client.post(
        "/bookmarks/new",
        data={
            "url": "https://example.com/work",
            "title": "Work item",
            "new_collections": "Work",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # Collection appears as a badge on the saved bookmark row.
    assert "Work" in body

    # Now the new-form should switch to "Or create a new collection".
    new_form = client.get("/bookmarks/new").get_data(as_text=True)
    assert "Or create a new collection" in new_form
    # Existing collection appears as a checkbox.
    assert 'name="collection_ids"' in new_form


def test_inline_collection_creation_reuses_existing_exact_name(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/a", "new_collections": "Reading"},
    )
    # Same exact name on the second save must reuse the existing collection.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/b", "new_collections": "Reading"},
    )
    body = client.get("/bookmarks/new").get_data(as_text=True)
    # Only one "Reading" collection should be rendered as a checkbox option.
    assert body.count('name="collection_ids"') == 1


def test_edit_can_create_collection_inline(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/x", "title": "X"})
    resp = client.post(
        "/bookmarks/1/edit",
        data={
            "url": "https://example.com/x",
            "title": "X",
            "new_collections": "Research",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Research" in resp.get_data(as_text=True)


def test_all_bookmarks_no_results_state_when_search_misses(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/a", "title": "Alpha"},
    )
    body = client.get("/bookmarks?q=zzznotfound").get_data(as_text=True)
    # No-results state — distinct from the real empty state.
    assert "No bookmarks match this view" in body
    assert "Clear search and filters" in body
    # The first-run empty-library copy must NOT appear.
    assert "Your bookmark library is empty" not in body
    assert "+ New Bookmark" not in body or body.count("+ New Bookmark") == 1  # only the topbar instance


def test_all_bookmarks_real_empty_state_when_truly_empty(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # Real empty state — first-run guidance.
    assert "Your bookmark library is empty" in body
    # No-results copy must NOT appear.
    assert "No bookmarks match this view" not in body
    assert "Clear search and filters" not in body


def test_favorites_no_results_state_when_search_misses(client):
    client.post(
        "/bookmarks/new",
        data={
            "url": "https://example.com/f",
            "title": "Faved",
            "is_favorite": "on",
        },
    )
    body = client.get("/favorites?q=zzznotfound").get_data(as_text=True)
    assert "No bookmarks match this view" in body
    assert "Clear search and filters" in body
    # The "what favorites are" copy must NOT appear.
    assert "No favorites yet" not in body


def test_favorites_real_empty_state_even_when_other_bookmarks_exist(client):
    # Creating a non-favorite bookmark must not turn the favorites screen
    # into a no-results state — favorites is its own scope.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/p", "title": "Plain"},
    )
    body = client.get("/favorites").get_data(as_text=True)
    assert "No favorites yet" in body
    assert "do not replace collections" in body
    assert "No bookmarks match this view" not in body
    assert "Clear search and filters" not in body


def test_no_results_clear_link_returns_to_unfiltered_view(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/k", "title": "Keep"},
    )
    body = client.get("/bookmarks?q=zzz").get_data(as_text=True)
    # The clear-link points back to the bare list URL.
    assert 'href="/bookmarks"' in body


def test_inline_collection_supports_multiple_comma_separated(client):
    client.post(
        "/bookmarks/new",
        data={
            "url": "https://example.com/m",
            "title": "Multi",
            "new_collections": "Work, Home",
        },
    )
    body = client.get("/bookmarks/new").get_data(as_text=True)
    assert "Work" in body
    assert "Home" in body


def test_create_bookmark_rejects_exact_duplicate_url(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/dup", "title": "First Save"})
    resp = client.post("/bookmarks/new", data={"url": "https://example.com/dup", "title": "Second Save"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "already saved" in body


def test_create_bookmark_duplicate_shows_link_to_existing(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/dup", "title": "The Original"})
    resp = client.post("/bookmarks/new", data={"url": "https://example.com/dup"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    # Link to the existing bookmark's edit page must be present.
    assert "/bookmarks/1/edit" in body
    assert "The Original" in body


def test_edit_bookmark_blocks_url_change_to_existing(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/one", "title": "One"})
    client.post("/bookmarks/new", data={"url": "https://example.com/two", "title": "Two"})
    resp = client.post(
        "/bookmarks/2/edit",
        data={"url": "https://example.com/one", "title": "Two"},
    )
    assert resp.status_code == 400
    assert "already saved" in resp.get_data(as_text=True)


def test_edit_bookmark_allows_resave_unchanged_url(client):
    client.post("/bookmarks/new", data={"url": "https://example.com/keep", "title": "Keep"})
    resp = client.post(
        "/bookmarks/1/edit",
        data={"url": "https://example.com/keep", "title": "Keep — edited title"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Bookmark updated" in resp.get_data(as_text=True)


def test_search_finds_bookmark_by_collection_name(client):
    # Title contains no hint of the search term — match must come from the collection name.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/sc", "title": "Something Unrelated", "new_collections": "WorkProject"},
    )
    client.post("/bookmarks/new", data={"url": "https://example.com/sd", "title": "Decoy Bookmark"})

    body = client.get("/bookmarks?q=WorkProject").get_data(as_text=True)
    assert "Something Unrelated" in body
    assert "Decoy Bookmark" not in body


def test_search_finds_bookmark_by_tag_name(client):
    # Title contains no hint of the search term — match must come from the tag name.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/st", "title": "Something Unrelated", "tags": "privacytopic"},
    )
    client.post("/bookmarks/new", data={"url": "https://example.com/su", "title": "Decoy Bookmark"})

    body = client.get("/bookmarks?q=privacytopic").get_data(as_text=True)
    assert "Something Unrelated" in body
    assert "Decoy Bookmark" not in body


def test_theme_toggle_present_in_topbar(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # The select element and all three options must be present.
    assert 'id="theme-toggle"' in body
    assert 'value="system"' in body
    assert 'value="light"' in body
    assert 'value="dark"' in body


def test_theme_anti_flash_script_present(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # The anti-flash script must run before the stylesheet to prevent FOUC.
    assert "tinybookmarker-theme" in body
    assert "data-theme" in body
    stylesheet_pos = body.find('rel="stylesheet"')
    antiflash_pos = body.find("tinybookmarker-theme")
    assert antiflash_pos < stylesheet_pos, "anti-flash script must appear before the stylesheet link"


# ── Collections screen ────────────────────────────────────────────────────────

def test_collections_empty_state(client):
    resp = client.get("/collections")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Collections" in body
    assert "No collections yet" in body
    # Empty state must distinguish collections from tags.
    assert "tags" in body.lower()


def test_collections_sidebar_link_active_on_collections_page(client):
    body = client.get("/collections").get_data(as_text=True)
    # The sidebar "Collections" link must carry the active class on this page.
    assert 'class="active"' in body
    # The active link must point to the collections route.
    assert 'href="/collections"' in body


def test_create_collection_via_collections_page(client):
    resp = client.post("/collections/new", data={"name": "Research"}, follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Research" in body
    assert "Collection created" in body


def test_collections_shows_bookmark_count(client):
    # Create a collection by saving a bookmark into it.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/c1", "title": "One", "new_collections": "Science"},
    )
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/c2", "title": "Two", "new_collections": "Science"},
    )
    body = client.get("/collections").get_data(as_text=True)
    assert "Science" in body
    assert "2 bookmarks" in body


def test_rename_collection(client):
    client.post("/collections/new", data={"name": "OldName"})
    # Find the collection id via the list.
    resp = client.get("/collections")
    assert "OldName" in resp.get_data(as_text=True)
    # Rename via POST to /collections/1/edit.
    resp = client.post("/collections/1/edit", data={"name": "NewName"}, follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "NewName" in body
    assert "Collection renamed" in body
    assert "OldName" not in body


def test_delete_collection_removes_collection_not_bookmarks(client):
    # Save a bookmark into a collection.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/del", "title": "Keep Me", "new_collections": "Temporary"},
    )
    # Delete the collection.
    resp = client.post("/collections/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Collection deleted" in body
    assert "Temporary" not in body
    # The bookmark must still exist in All Bookmarks.
    bm_body = client.get("/bookmarks").get_data(as_text=True)
    assert "Keep Me" in bm_body


def test_create_collection_rejects_empty_name(client):
    resp = client.post("/collections/new", data={"name": ""})
    assert resp.status_code == 400
    assert "required" in resp.get_data(as_text=True).lower()


def test_create_collection_rejects_duplicate_name(client):
    client.post("/collections/new", data={"name": "Unique"})
    resp = client.post("/collections/new", data={"name": "Unique"})
    assert resp.status_code == 400
    assert "already exists" in resp.get_data(as_text=True)


# ── Tags screen ───────────────────────────────────────────────────────────────

def test_tags_empty_state(client):
    resp = client.get("/tags")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Tags" in body
    assert "No tags yet" in body
    # Empty state must distinguish tags from collections.
    assert "collections" in body.lower()


def test_tags_sidebar_link_active_on_tags_page(client):
    body = client.get("/tags").get_data(as_text=True)
    # The sidebar "Tags" link must carry the active class on this page.
    assert 'class="active"' in body
    assert 'href="/tags"' in body


def test_tags_shows_bookmark_count(client):
    # Create tags by saving bookmarks with them.
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/t1", "title": "One", "tags": "python"},
    )
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/t2", "title": "Two", "tags": "python"},
    )
    body = client.get("/tags").get_data(as_text=True)
    assert "python" in body
    assert "2 bookmarks" in body


def test_tags_no_create_form(client):
    # Tags screen intentionally has no standalone create form.
    body = client.get("/tags").get_data(as_text=True)
    # There must be no POST target for /tags/new or similar on this page.
    assert 'action="/tags/new"' not in body
    assert 'name="name"' not in body


def test_rename_tag(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/tr", "title": "Tagged", "tags": "oldlabel"},
    )
    resp = client.post("/tags/1/edit", data={"name": "newlabel"}, follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "newlabel" in body
    assert "Tag renamed" in body
    assert "oldlabel" not in body


def test_delete_tag_removes_tag_not_bookmarks(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/td", "title": "Keep Me", "tags": "temporary"},
    )
    resp = client.post("/tags/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Tag deleted" in body
    assert "temporary" not in body
    # The bookmark must still exist.
    bm_body = client.get("/bookmarks").get_data(as_text=True)
    assert "Keep Me" in bm_body


def test_rename_tag_rejects_empty_name(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/te", "title": "Tagged", "tags": "notempty"},
    )
    resp = client.post("/tags/1/edit", data={"name": ""})
    assert resp.status_code == 400
    assert "required" in resp.get_data(as_text=True).lower()


def test_rename_tag_rejects_duplicate_name(client):
    client.post(
        "/bookmarks/new",
        data={"url": "https://example.com/td1", "title": "A", "tags": "alpha, beta"},
    )
    # Try renaming "alpha" (id=1) to "beta" — should fail.
    resp = client.post("/tags/1/edit", data={"name": "beta"})
    assert resp.status_code == 400
    assert "already exists" in resp.get_data(as_text=True)


# ── Duplicates screen ─────────────────────────────────────────────────────────

def _insert_bookmark(app, url, title=""):
    """Insert a bookmark directly into the DB, bypassing the duplicate-check route."""
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(app.config["DATABASE"])
    conn.execute(
        "INSERT INTO bookmarks (url, title) VALUES (?, ?)",
        (url, title or url),
    )
    conn.commit()
    conn.close()


def test_duplicates_empty_state(client):
    resp = client.get("/duplicates")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Duplicates" in body
    assert "No duplicates found" in body
    # Empty state must mention exact URL matching so users understand the scope.
    assert "exact" in body.lower()


def test_duplicates_sidebar_link_active_on_duplicates_page(client):
    body = client.get("/duplicates").get_data(as_text=True)
    assert 'class="active"' in body
    assert 'href="/duplicates"' in body


def test_duplicates_shows_group_for_exact_url_match(client, app):
    _insert_bookmark(app, "https://dup.example.com/page", "First Save")
    _insert_bookmark(app, "https://dup.example.com/page", "Second Save")

    body = client.get("/duplicates").get_data(as_text=True)
    assert "First Save" in body
    assert "Second Save" in body
    assert "https://dup.example.com/page" in body
    # Group count must be visible.
    assert "2 bookmarks" in body


def test_duplicates_ignores_unique_urls(client, app):
    _insert_bookmark(app, "https://unique-a.example.com/", "Unique A")
    _insert_bookmark(app, "https://unique-b.example.com/", "Unique B")

    body = client.get("/duplicates").get_data(as_text=True)
    assert "No duplicates found" in body
    assert "Unique A" not in body
    assert "Unique B" not in body


def test_duplicates_does_not_group_different_urls(client, app):
    # Superficially similar but distinct URLs must not be grouped.
    _insert_bookmark(app, "https://example.com/page", "HTTP version")
    _insert_bookmark(app, "https://example.com/page/", "Trailing slash version")

    body = client.get("/duplicates").get_data(as_text=True)
    assert "No duplicates found" in body


def test_duplicates_delete_returns_to_duplicates_page(client, app):
    _insert_bookmark(app, "https://dup2.example.com/", "Alpha")
    _insert_bookmark(app, "https://dup2.example.com/", "Beta")

    # Delete bookmark id=1 via the existing delete route with next=/duplicates.
    resp = client.post(
        "/bookmarks/1/delete",
        data={"next": "/duplicates"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # After deleting one, the group disappears (only one left — no longer a duplicate).
    assert "No duplicates found" in body
    # The surviving bookmark must still exist in All Bookmarks.
    bm_body = client.get("/bookmarks").get_data(as_text=True)
    assert "Beta" in bm_body


def test_duplicates_shows_edit_link_for_each_bookmark(client, app):
    _insert_bookmark(app, "https://dup3.example.com/", "Edit Test A")
    _insert_bookmark(app, "https://dup3.example.com/", "Edit Test B")

    body = client.get("/duplicates").get_data(as_text=True)
    # Both bookmarks must have an edit link.
    assert "/bookmarks/1/edit" in body
    assert "/bookmarks/2/edit" in body


def test_delete_duplicate_succeeds_when_another_copy_remains(client, app):
    _insert_bookmark(app, "https://safe.example.com/", "Copy One")
    _insert_bookmark(app, "https://safe.example.com/", "Copy Two")

    resp = client.post("/duplicates/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Bookmark deleted" in body
    # The surviving copy must still exist.
    bm_body = client.get("/bookmarks").get_data(as_text=True)
    assert "Copy Two" in bm_body


def test_delete_duplicate_blocked_when_last_copy(client, app):
    # Insert only one bookmark with a URL that has no duplicate.
    # Then try to delete it via the safe duplicate-delete route.
    _insert_bookmark(app, "https://last.example.com/", "Only Copy")

    resp = client.post("/duplicates/1/delete", follow_redirects=True)
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # Must show an error flash — deletion was blocked.
    assert "only remaining" in body
    # The bookmark must still exist.
    bm_body = client.get("/bookmarks").get_data(as_text=True)
    assert "Only Copy" in bm_body
