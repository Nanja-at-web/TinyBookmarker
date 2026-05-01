import sqlite3
from typing import Iterable
from urllib.parse import urlparse


def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


def split_tag_input(raw: str) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for chunk in raw.replace(";", ",").split(","):
        name = chunk.strip()
        if name and name not in parts:
            parts.append(name)
    return parts


def list_bookmarks(
    db: sqlite3.Connection,
    *,
    favorites_only: bool = False,
    unsorted_only: bool = False,
    collection_id: int | None = None,
    tag_id: int | None = None,
    query: str = "",
    sort: str = "newest",
) -> list[dict]:
    sql = ["SELECT b.* FROM bookmarks b"]
    params: list = []
    where: list[str] = []

    if collection_id is not None:
        sql.append("JOIN bookmark_collections bc ON bc.bookmark_id = b.id")
        where.append("bc.collection_id = ?")
        params.append(collection_id)
    if tag_id is not None:
        sql.append("JOIN bookmark_tags bt ON bt.bookmark_id = b.id")
        where.append("bt.tag_id = ?")
        params.append(tag_id)
    if favorites_only:
        where.append("b.is_favorite = 1")
    if unsorted_only:
        # "Unsorted" = saved but not yet structurally organized: no collection AND no tag.
        where.append(
            "NOT EXISTS (SELECT 1 FROM bookmark_collections WHERE bookmark_id = b.id) "
            "AND NOT EXISTS (SELECT 1 FROM bookmark_tags WHERE bookmark_id = b.id)"
        )
    if query:
        like = f"%{query}%"
        where.append(
            "(b.title LIKE ? OR b.url LIKE ? OR b.description LIKE ?"
            " OR EXISTS (SELECT 1 FROM bookmark_collections bc2"
            "            JOIN collections c2 ON c2.id = bc2.collection_id"
            "            WHERE bc2.bookmark_id = b.id AND c2.name LIKE ?)"
            " OR EXISTS (SELECT 1 FROM bookmark_tags bt2"
            "            JOIN tags t2 ON t2.id = bt2.tag_id"
            "            WHERE bt2.bookmark_id = b.id AND t2.name LIKE ?))"
        )
        params.extend([like, like, like, like, like])

    if where:
        sql.append("WHERE " + " AND ".join(where))

    order = {
        "newest": "b.created_at DESC, b.id DESC",
        "oldest": "b.created_at ASC, b.id ASC",
        "title": "LOWER(b.title) ASC, b.id ASC",
    }.get(sort, "b.created_at DESC, b.id DESC")
    sql.append(f"ORDER BY {order}")

    rows = db.execute(" ".join(sql), params).fetchall()
    bookmarks = [dict(r) for r in rows]
    if bookmarks:
        ids = [b["id"] for b in bookmarks]
        _attach_assignments(db, bookmarks, ids)
    for b in bookmarks:
        b["domain"] = domain_of(b["url"])
    return bookmarks


def _attach_assignments(db: sqlite3.Connection, bookmarks: list[dict], ids: Iterable[int]) -> None:
    ids = list(ids)
    by_id = {b["id"]: b for b in bookmarks}
    for b in bookmarks:
        b["collections"] = []
        b["tags"] = []

    if not ids:
        return
    qmarks = ",".join("?" * len(ids))

    coll_rows = db.execute(
        f"""
        SELECT bc.bookmark_id, c.id, c.name
          FROM bookmark_collections bc
          JOIN collections c ON c.id = bc.collection_id
         WHERE bc.bookmark_id IN ({qmarks})
         ORDER BY LOWER(c.name)
        """,
        ids,
    ).fetchall()
    for r in coll_rows:
        by_id[r["bookmark_id"]]["collections"].append({"id": r["id"], "name": r["name"]})

    tag_rows = db.execute(
        f"""
        SELECT bt.bookmark_id, t.id, t.name
          FROM bookmark_tags bt
          JOIN tags t ON t.id = bt.tag_id
         WHERE bt.bookmark_id IN ({qmarks})
         ORDER BY LOWER(t.name)
        """,
        ids,
    ).fetchall()
    for r in tag_rows:
        by_id[r["bookmark_id"]]["tags"].append({"id": r["id"], "name": r["name"]})


def find_bookmark_by_url(db: sqlite3.Connection, url: str) -> dict | None:
    """Return a minimal dict {id, title, url} if a bookmark with this exact URL exists."""
    row = db.execute(
        "SELECT id, title, url FROM bookmarks WHERE url = ?", (url,)
    ).fetchone()
    return dict(row) if row else None


def get_bookmark(db: sqlite3.Connection, bookmark_id: int) -> dict | None:
    row = db.execute("SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)).fetchone()
    if row is None:
        return None
    bookmark = dict(row)
    _attach_assignments(db, [bookmark], [bookmark["id"]])
    bookmark["domain"] = domain_of(bookmark["url"])
    return bookmark


def create_bookmark(
    db: sqlite3.Connection,
    *,
    url: str,
    title: str,
    description: str,
    is_favorite: bool,
    collection_ids: list[int],
    new_collection_names: list[str] | None = None,
    tag_names: list[str],
) -> int:
    cur = db.execute(
        "INSERT INTO bookmarks (url, title, description, is_favorite) VALUES (?, ?, ?, ?)",
        (url, title, description, 1 if is_favorite else 0),
    )
    bookmark_id = cur.lastrowid
    _set_collections(db, bookmark_id, collection_ids, new_collection_names or [])
    _set_tags(db, bookmark_id, tag_names)
    db.commit()
    return bookmark_id


def update_bookmark(
    db: sqlite3.Connection,
    bookmark_id: int,
    *,
    url: str,
    title: str,
    description: str,
    is_favorite: bool,
    collection_ids: list[int],
    new_collection_names: list[str] | None = None,
    tag_names: list[str],
) -> None:
    db.execute(
        """
        UPDATE bookmarks
           SET url = ?, title = ?, description = ?, is_favorite = ?, updated_at = datetime('now')
         WHERE id = ?
        """,
        (url, title, description, 1 if is_favorite else 0, bookmark_id),
    )
    _set_collections(db, bookmark_id, collection_ids, new_collection_names or [])
    _set_tags(db, bookmark_id, tag_names)
    db.commit()


def delete_bookmark(db: sqlite3.Connection, bookmark_id: int) -> None:
    db.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
    db.commit()


def toggle_favorite(db: sqlite3.Connection, bookmark_id: int) -> bool | None:
    row = db.execute("SELECT is_favorite FROM bookmarks WHERE id = ?", (bookmark_id,)).fetchone()
    if row is None:
        return None
    new_state = 0 if row["is_favorite"] else 1
    db.execute(
        "UPDATE bookmarks SET is_favorite = ?, updated_at = datetime('now') WHERE id = ?",
        (new_state, bookmark_id),
    )
    db.commit()
    return bool(new_state)


def _set_collections(
    db: sqlite3.Connection,
    bookmark_id: int,
    collection_ids: list[int],
    new_collection_names: list[str] | None = None,
) -> None:
    db.execute("DELETE FROM bookmark_collections WHERE bookmark_id = ?", (bookmark_id,))
    ids: list[int] = list(collection_ids)
    for name in new_collection_names or []:
        ids.append(get_or_create_collection(db, name))
    if not ids:
        return
    db.executemany(
        "INSERT OR IGNORE INTO bookmark_collections (bookmark_id, collection_id) VALUES (?, ?)",
        [(bookmark_id, cid) for cid in ids],
    )


def _set_tags(db: sqlite3.Connection, bookmark_id: int, tag_names: list[str]) -> None:
    db.execute("DELETE FROM bookmark_tags WHERE bookmark_id = ?", (bookmark_id,))
    tag_ids: list[int] = []
    for name in tag_names:
        tag_ids.append(get_or_create_tag(db, name))
    if tag_ids:
        db.executemany(
            "INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
            [(bookmark_id, tid) for tid in tag_ids],
        )


def get_or_create_tag(db: sqlite3.Connection, name: str) -> int:
    name = name.strip()
    row = db.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if row is not None:
        return row["id"]
    cur = db.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    return cur.lastrowid


def list_collections(db: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in db.execute("SELECT id, name FROM collections ORDER BY LOWER(name)")]


def list_tags(db: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in db.execute("SELECT id, name FROM tags ORDER BY LOWER(name)")]


def get_or_create_collection(db: sqlite3.Connection, name: str) -> int:
    name = name.strip()
    row = db.execute("SELECT id FROM collections WHERE name = ?", (name,)).fetchone()
    if row is not None:
        return row["id"]
    cur = db.execute("INSERT INTO collections (name) VALUES (?)", (name,))
    return cur.lastrowid
