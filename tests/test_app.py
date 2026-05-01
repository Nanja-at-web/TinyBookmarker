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


def test_inbox_filter_shows_only_unsorted(client):
    client.post("/bookmarks/new", data={"url": "https://x.example.com/", "title": "Sorted", "tags": "t1"})
    client.post("/bookmarks/new", data={"url": "https://y.example.com/", "title": "Unsorted"})

    resp = client.get("/bookmarks?filter=inbox")
    body = resp.get_data(as_text=True)
    assert "Unsorted" in body
    assert "Sorted" not in body


def test_404_on_unknown_bookmark(client):
    assert client.get("/bookmarks/999/edit").status_code == 404
    assert client.post("/bookmarks/999/delete").status_code == 404
    assert client.post("/bookmarks/999/toggle-favorite").status_code == 404
