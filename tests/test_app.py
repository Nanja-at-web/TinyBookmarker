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


def test_theme_toggle_options_have_status_icons(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # Each option must carry its status symbol so the active state is visible.
    assert '⊙ System' in body
    assert '☀ Light' in body
    assert '☽ Dark' in body


def test_theme_anti_flash_script_present(client):
    body = client.get("/bookmarks").get_data(as_text=True)
    # The anti-flash script must run before the stylesheet to prevent FOUC.
    assert "tinybookmarker-theme" in body
    assert "data-theme" in body
    stylesheet_pos = body.find('rel="stylesheet"')
    antiflash_pos = body.find("tinybookmarker-theme")
    assert antiflash_pos < stylesheet_pos, "anti-flash script must appear before the stylesheet link"


# ── CSRF protection ───────────────────────────────────────────────────────────

def test_csrf_post_without_token_is_rejected(app):
    # Raw client — no auto-injected token — simulates a cross-site request.
    raw = app.test_client()
    resp = raw.post("/bookmarks/new", data={"url": "https://example.com"})
    assert resp.status_code == 403


def test_csrf_post_with_wrong_token_is_rejected(app):
    raw = app.test_client()
    with raw.session_transaction() as sess:
        sess["csrf_token"] = "correct-token"
    resp = raw.post("/bookmarks/new", data={"url": "https://example.com", "csrf_token": "wrong-token"})
    assert resp.status_code == 403


def test_csrf_post_with_valid_token_proceeds(app):
    raw = app.test_client()
    with raw.session_transaction() as sess:
        sess["csrf_token"] = "valid-token"
    # Empty URL triggers a 400 (form validation), not 403 — CSRF check passed.
    resp = raw.post("/bookmarks/new", data={"url": "", "csrf_token": "valid-token"})
    assert resp.status_code == 400


def test_csrf_token_hidden_field_present_in_forms(client):
    # Pages that always render a POST form must embed the hidden CSRF field.
    # /bookmarks/new always has the save form; /collections always has the
    # create-collection form.  /tags only shows delete forms when tags exist,
    # so it is excluded from this always-available check.
    for path in ["/bookmarks/new", "/collections"]:
        body = client.get(path).get_data(as_text=True)
        assert 'name="csrf_token"' in body, f"csrf_token field missing on {path}"


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_auth_disabled_when_no_password_set(app):
    # Default app fixture has no password — every route is publicly accessible.
    raw = app.test_client()
    assert raw.get("/bookmarks").status_code == 200


def test_auth_login_page_redirects_to_bookmarks_when_disabled(app):
    raw = app.test_client()
    resp = raw.get("/login")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/bookmarks")


def test_auth_redirects_unauthenticated_request_to_login(auth_app):
    raw = auth_app.test_client()
    resp = raw.get("/bookmarks")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_auth_login_page_is_accessible_without_session(auth_app):
    raw = auth_app.test_client()
    resp = raw.get("/login")
    assert resp.status_code == 200
    assert "Password" in resp.get_data(as_text=True)


def test_auth_wrong_password_returns_401(auth_app):
    raw = auth_app.test_client()
    with raw.session_transaction() as sess:
        sess["csrf_token"] = "tok"
    resp = raw.post("/login", data={"password": "wrong", "csrf_token": "tok"})
    assert resp.status_code == 401
    assert "Wrong password" in resp.get_data(as_text=True)


def test_auth_correct_password_sets_session_and_redirects(auth_app):
    raw = auth_app.test_client()
    with raw.session_transaction() as sess:
        sess["csrf_token"] = "tok"
    resp = raw.post("/login", data={"password": "testpass", "csrf_token": "tok"})
    assert resp.status_code == 302
    with raw.session_transaction() as sess:
        assert sess.get("authenticated") is True


def test_auth_after_login_can_access_protected_routes(auth_app):
    from conftest import CsrfTestClient
    c = CsrfTestClient(auth_app.test_client())
    with c._client.session_transaction() as sess:
        sess["authenticated"] = True
    assert c.get("/bookmarks").status_code == 200


def test_auth_logout_clears_session_and_redirects_to_login(auth_app):
    from conftest import CsrfTestClient
    c = CsrfTestClient(auth_app.test_client())
    with c._client.session_transaction() as sess:
        sess["authenticated"] = True
    resp = c.post("/logout")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
    with c._client.session_transaction() as sess:
        assert not sess.get("authenticated")


def test_auth_login_preserves_next_param(auth_app):
    raw = auth_app.test_client()
    with raw.session_transaction() as sess:
        sess["csrf_token"] = "tok"
    resp = raw.post(
        "/login?next=/collections",
        data={"password": "testpass", "csrf_token": "tok", "next": "/collections"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/collections")


def test_auth_logout_button_visible_when_authenticated(auth_app):
    from conftest import CsrfTestClient
    c = CsrfTestClient(auth_app.test_client())
    with c._client.session_transaction() as sess:
        sess["authenticated"] = True
    body = c.get("/bookmarks").get_data(as_text=True)
    assert "Logout" in body


def test_auth_logout_button_absent_when_auth_disabled(client):
    # When no password is set the logout form must not appear.
    body = client.get("/bookmarks").get_data(as_text=True)
    assert "Logout" not in body


# ── Session cookie settings ───────────────────────────────────────────────────

def test_session_cookie_httponly_is_true(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True


def test_session_cookie_samesite_is_lax(app):
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_session_cookie_secure_is_false_by_default(app):
    # Dev default — no TINYBOOKMARKER_SECURE_COOKIES env var set.
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_session_cookie_secure_enabled_via_config(tmp_path):
    # Simulate production: pass SESSION_COOKIE_SECURE=True via config dict
    # (same code path used when TINYBOOKMARKER_SECURE_COOKIES env var is set).
    import os, tempfile
    from app import create_app as _create
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        a = _create({
            "TESTING": True,
            "DATABASE": path,
            "SECRET_KEY": "test",
            "SESSION_COOKIE_SECURE": True,
        })
        assert a.config["SESSION_COOKIE_SECURE"] is True
    finally:
        os.unlink(path)


def test_session_cookie_secure_enabled_via_env(monkeypatch, tmp_path):
    monkeypatch.setenv("TINYBOOKMARKER_SECURE_COOKIES", "true")
    import os, tempfile
    from app import create_app as _create
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        a = _create({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
        assert a.config["SESSION_COOKIE_SECURE"] is True
    finally:
        os.unlink(path)


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


# ── Sorting ───────────────────────────────────────────────────────────────────

def test_collections_default_sort_is_name(client):
    client.post("/collections/new", data={"name": "Zebra"})
    client.post("/collections/new", data={"name": "Alpha"})
    body = client.get("/collections").get_data(as_text=True)
    assert body.index("Alpha") < body.index("Zebra")


def test_collections_sort_by_count(client):
    # "Big" gets 2 bookmarks, "Small" gets 1 — sort=count should list Big first.
    client.post("/bookmarks/new", data={"url": "https://a.com/1", "title": "A1", "new_collections": "Big"})
    client.post("/bookmarks/new", data={"url": "https://a.com/2", "title": "A2", "new_collections": "Big"})
    client.post("/bookmarks/new", data={"url": "https://a.com/3", "title": "A3", "new_collections": "Small"})
    body = client.get("/collections?sort=count").get_data(as_text=True)
    assert body.index("Big") < body.index("Small")


def test_collections_sort_select_reflects_current_sort(client):
    client.post("/collections/new", data={"name": "Test"})
    body = client.get("/collections?sort=count").get_data(as_text=True)
    # The count option must be marked selected.
    assert 'value="count"' in body
    assert 'selected' in body


def test_tags_default_sort_is_name(client):
    client.post("/bookmarks/new", data={"url": "https://b.com/1", "title": "B1", "tags": "zebra, alpha"})
    body = client.get("/tags").get_data(as_text=True)
    assert body.index("alpha") < body.index("zebra")


def test_tags_sort_by_count(client):
    # "popular" gets 2 bookmarks, "rare" gets 1.
    client.post("/bookmarks/new", data={"url": "https://c.com/1", "title": "C1", "tags": "popular"})
    client.post("/bookmarks/new", data={"url": "https://c.com/2", "title": "C2", "tags": "popular"})
    client.post("/bookmarks/new", data={"url": "https://c.com/3", "title": "C3", "tags": "rare"})
    body = client.get("/tags?sort=count").get_data(as_text=True)
    assert body.index("popular") < body.index("rare")


def test_duplicates_default_sort_is_url(client, app):
    _insert_bookmark(app, "https://zzz.example.com/", "Z1")
    _insert_bookmark(app, "https://zzz.example.com/", "Z2")
    _insert_bookmark(app, "https://aaa.example.com/", "A1")
    _insert_bookmark(app, "https://aaa.example.com/", "A2")
    body = client.get("/duplicates").get_data(as_text=True)
    assert body.index("aaa.example.com") < body.index("zzz.example.com")


def test_duplicates_sort_by_size(client, app):
    # "big" group has 3 copies, "small" group has 2.
    _insert_bookmark(app, "https://big.example.com/", "B1")
    _insert_bookmark(app, "https://big.example.com/", "B2")
    _insert_bookmark(app, "https://big.example.com/", "B3")
    _insert_bookmark(app, "https://small.example.com/", "S1")
    _insert_bookmark(app, "https://small.example.com/", "S2")
    body = client.get("/duplicates?sort=size").get_data(as_text=True)
    assert body.index("big.example.com") < body.index("small.example.com")


# ── Descending / reverse sort options ────────────────────────────────────────

def test_bookmarks_sort_title_desc(client):
    client.post("/bookmarks/new", data={"url": "https://d.com/1", "title": "Alpha"})
    client.post("/bookmarks/new", data={"url": "https://d.com/2", "title": "Zebra"})
    body = client.get("/bookmarks?sort=title_desc").get_data(as_text=True)
    assert body.index("Zebra") < body.index("Alpha")


def test_favorites_sort_title_desc(client):
    client.post("/bookmarks/new", data={"url": "https://e.com/1", "title": "Alpha", "is_favorite": "on"})
    client.post("/bookmarks/new", data={"url": "https://e.com/2", "title": "Zebra", "is_favorite": "on"})
    body = client.get("/favorites?sort=title_desc").get_data(as_text=True)
    assert body.index("Zebra") < body.index("Alpha")


def test_collections_sort_name_desc(client):
    client.post("/collections/new", data={"name": "Alpha"})
    client.post("/collections/new", data={"name": "Zebra"})
    body = client.get("/collections?sort=name_desc").get_data(as_text=True)
    assert body.index("Zebra") < body.index("Alpha")


def test_collections_sort_count_asc(client):
    # "Small" has 1 bookmark, "Big" has 2 — fewest first → Small before Big.
    client.post("/bookmarks/new", data={"url": "https://f.com/1", "title": "F1", "new_collections": "Big"})
    client.post("/bookmarks/new", data={"url": "https://f.com/2", "title": "F2", "new_collections": "Big"})
    client.post("/bookmarks/new", data={"url": "https://f.com/3", "title": "F3", "new_collections": "Small"})
    body = client.get("/collections?sort=count_asc").get_data(as_text=True)
    assert body.index("Small") < body.index("Big")


def test_tags_sort_name_desc(client):
    client.post("/bookmarks/new", data={"url": "https://g.com/1", "title": "G1", "tags": "alpha, zebra"})
    body = client.get("/tags?sort=name_desc").get_data(as_text=True)
    assert body.index("zebra") < body.index("alpha")


def test_tags_sort_count_asc(client):
    # "rare" has 1 bookmark, "popular" has 2 — fewest first → rare before popular.
    client.post("/bookmarks/new", data={"url": "https://h.com/1", "title": "H1", "tags": "popular"})
    client.post("/bookmarks/new", data={"url": "https://h.com/2", "title": "H2", "tags": "popular"})
    client.post("/bookmarks/new", data={"url": "https://h.com/3", "title": "H3", "tags": "rare"})
    body = client.get("/tags?sort=count_asc").get_data(as_text=True)
    assert body.index("rare") < body.index("popular")


def test_duplicates_sort_url_desc(client, app):
    _insert_bookmark(app, "https://aaa.sort-test.com/", "A1")
    _insert_bookmark(app, "https://aaa.sort-test.com/", "A2")
    _insert_bookmark(app, "https://zzz.sort-test.com/", "Z1")
    _insert_bookmark(app, "https://zzz.sort-test.com/", "Z2")
    body = client.get("/duplicates?sort=url_desc").get_data(as_text=True)
    assert body.index("zzz.sort-test.com") < body.index("aaa.sort-test.com")


def test_duplicates_sort_size_asc(client, app):
    # "big" has 3, "small" has 2 — smallest first → small before big.
    _insert_bookmark(app, "https://big.sort-test.com/", "B1")
    _insert_bookmark(app, "https://big.sort-test.com/", "B2")
    _insert_bookmark(app, "https://big.sort-test.com/", "B3")
    _insert_bookmark(app, "https://small.sort-test.com/", "S1")
    _insert_bookmark(app, "https://small.sort-test.com/", "S2")
    body = client.get("/duplicates?sort=size_asc").get_data(as_text=True)
    assert body.index("small.sort-test.com") < body.index("big.sort-test.com")
