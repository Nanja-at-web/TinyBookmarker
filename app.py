import os

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

import bookmarks as bm
import db


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("TINYBOOKMARKER_SECRET", "dev-secret-change-me"),
        DATABASE=os.environ.get(
            "TINYBOOKMARKER_DB",
            os.path.join(app.instance_path, "tinybookmarker.sqlite"),
        ),
    )
    if config:
        app.config.update(config)

    db.init_db(app)
    db.init_app(app)

    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return redirect(url_for("all_bookmarks"))

    @app.get("/bookmarks")
    def all_bookmarks():
        conn = db.get_db()
        params = _parse_list_params(request.args)
        items = bm.list_bookmarks(conn, **params)
        return render_template(
            "bookmarks_list.html",
            page="all_bookmarks",
            page_title="All Bookmarks",
            page_subtitle="Your full bookmark library",
            items=items,
            collections=bm.list_collections(conn),
            tags=bm.list_tags(conn),
            filters=params,
            is_filtered=_is_filtered(params),
            empty_kind="all",
        )

    @app.get("/favorites")
    def favorites():
        conn = db.get_db()
        params = _parse_list_params(request.args)
        params["favorites_only"] = True
        items = bm.list_bookmarks(conn, **params)
        return render_template(
            "bookmarks_list.html",
            page="favorites",
            page_title="Favorites",
            page_subtitle="Your personal quick-access bookmarks.",
            items=items,
            collections=bm.list_collections(conn),
            tags=bm.list_tags(conn),
            filters=params,
            is_filtered=_is_filtered(params),
            empty_kind="favorites",
        )

    @app.route("/bookmarks/new", methods=["GET", "POST"])
    def new_bookmark():
        conn = db.get_db()
        if request.method == "POST":
            data, errors = _parse_form(request.form)
            duplicate_of = None
            if not errors:
                duplicate_of = bm.find_bookmark_by_url(conn, data["url"])
                if duplicate_of:
                    errors["url"] = "This URL is already saved as a bookmark."
            if errors:
                return render_template(
                    "bookmark_form.html",
                    page="new_bookmark",
                    page_title="New Bookmark",
                    page_subtitle="Save a bookmark now. You can organize it immediately or review it later.",
                    form=data,
                    errors=errors,
                    collections=bm.list_collections(conn),
                    is_edit=False,
                    duplicate_of=duplicate_of,
                ), 400

            bm.create_bookmark(
                conn,
                url=data["url"],
                title=data["title"],
                description=data["description"],
                is_favorite=data["is_favorite"],
                collection_ids=data["collection_ids"],
                new_collection_names=data["new_collection_names"],
                tag_names=data["tag_names"],
            )
            flash("Bookmark saved.", "success")
            return redirect(url_for("all_bookmarks"))

        prefill_url = request.args.get("url", "").strip()
        return render_template(
            "bookmark_form.html",
            page="new_bookmark",
            page_title="New Bookmark",
            page_subtitle="Save a bookmark now. You can organize it immediately or review it later.",
            form={
                "url": prefill_url,
                "title": "",
                "description": "",
                "is_favorite": False,
                "collection_ids": [],
                "new_collection_names": [],
                "tag_names": [],
            },
            errors={},
            collections=bm.list_collections(conn),
            is_edit=False,
            duplicate_of=None,
        )

    @app.route("/bookmarks/<int:bookmark_id>/edit", methods=["GET", "POST"])
    def edit_bookmark(bookmark_id: int):
        conn = db.get_db()
        existing = bm.get_bookmark(conn, bookmark_id)
        if existing is None:
            abort(404)

        if request.method == "POST":
            data, errors = _parse_form(request.form)
            duplicate_of = None
            if not errors:
                dup = bm.find_bookmark_by_url(conn, data["url"])
                if dup and dup["id"] != bookmark_id:
                    duplicate_of = dup
                    errors["url"] = "This URL is already saved as a bookmark."
            if errors:
                return render_template(
                    "bookmark_form.html",
                    page="edit_bookmark",
                    page_title="Edit Bookmark",
                    page_subtitle="Review and update this bookmark.",
                    form=data,
                    errors=errors,
                    collections=bm.list_collections(conn),
                    is_edit=True,
                    bookmark=existing,
                    duplicate_of=duplicate_of,
                ), 400

            bm.update_bookmark(
                conn,
                bookmark_id,
                url=data["url"],
                title=data["title"],
                description=data["description"],
                is_favorite=data["is_favorite"],
                collection_ids=data["collection_ids"],
                new_collection_names=data["new_collection_names"],
                tag_names=data["tag_names"],
            )
            flash("Bookmark updated.", "success")
            return redirect(url_for("all_bookmarks"))

        return render_template(
            "bookmark_form.html",
            page="edit_bookmark",
            page_title="Edit Bookmark",
            page_subtitle="Review and update this bookmark.",
            form={
                "url": existing["url"],
                "title": existing["title"],
                "description": existing["description"],
                "is_favorite": bool(existing["is_favorite"]),
                "collection_ids": [c["id"] for c in existing["collections"]],
                "new_collection_names": [],
                "tag_names": [t["name"] for t in existing["tags"]],
            },
            errors={},
            collections=bm.list_collections(conn),
            is_edit=True,
            duplicate_of=None,
            bookmark=existing,
        )

    @app.post("/bookmarks/<int:bookmark_id>/delete")
    def delete_bookmark(bookmark_id: int):
        conn = db.get_db()
        if bm.get_bookmark(conn, bookmark_id) is None:
            abort(404)
        bm.delete_bookmark(conn, bookmark_id)
        flash("Bookmark deleted.", "success")
        return redirect(request.form.get("next") or url_for("all_bookmarks"))

    @app.post("/bookmarks/<int:bookmark_id>/toggle-favorite")
    def toggle_favorite(bookmark_id: int):
        conn = db.get_db()
        result = bm.toggle_favorite(conn, bookmark_id)
        if result is None:
            abort(404)
        return redirect(request.form.get("next") or url_for("all_bookmarks"))

    # ── Collections ──────────────────────────────────────────────────────────

    @app.get("/collections")
    def collections():
        conn = db.get_db()
        sort = request.args.get("sort", "name")
        if sort not in {"name", "count"}:
            sort = "name"
        return render_template(
            "collections.html",
            page="collections",
            page_title="Collections",
            collections=bm.list_collections_with_counts(conn, sort=sort),
            sort=sort,
            create_error=None,
            create_name="",
        )

    @app.post("/collections/new")
    def new_collection():
        conn = db.get_db()
        name = (request.form.get("name") or "").strip()
        _id, error = bm.create_collection(conn, name)
        if error:
            return render_template(
                "collections.html",
                page="collections",
                page_title="Collections",
                collections=bm.list_collections_with_counts(conn),
                create_error=error,
                create_name=name,
            ), 400
        flash("Collection created.", "success")
        return redirect(url_for("collections"))

    @app.route("/collections/<int:collection_id>/edit", methods=["GET", "POST"])
    def edit_collection(collection_id: int):
        conn = db.get_db()
        collection = bm.get_collection(conn, collection_id)
        if collection is None:
            abort(404)
        if request.method == "POST":
            new_name = (request.form.get("name") or "").strip()
            error = bm.rename_collection(conn, collection_id, new_name)
            if error:
                return render_template(
                    "collection_rename.html",
                    page="collections",
                    page_title="Rename Collection",
                    collection=collection,
                    form_name=new_name,
                    error=error,
                ), 400
            flash("Collection renamed.", "success")
            return redirect(url_for("collections"))
        return render_template(
            "collection_rename.html",
            page="collections",
            page_title="Rename Collection",
            collection=collection,
            form_name=collection["name"],
            error=None,
        )

    @app.post("/collections/<int:collection_id>/delete")
    def delete_collection(collection_id: int):
        conn = db.get_db()
        if bm.get_collection(conn, collection_id) is None:
            abort(404)
        bm.delete_collection(conn, collection_id)
        flash("Collection deleted.", "success")
        return redirect(url_for("collections"))

    # ── Tags ─────────────────────────────────────────────────────────────────

    @app.get("/tags")
    def tags():
        conn = db.get_db()
        sort = request.args.get("sort", "name")
        if sort not in {"name", "count"}:
            sort = "name"
        return render_template(
            "tags.html",
            page="tags",
            page_title="Tags",
            tags=bm.list_tags_with_counts(conn, sort=sort),
            sort=sort,
        )

    @app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
    def edit_tag(tag_id: int):
        conn = db.get_db()
        tag = bm.get_tag(conn, tag_id)
        if tag is None:
            abort(404)
        if request.method == "POST":
            new_name = (request.form.get("name") or "").strip()
            error = bm.rename_tag(conn, tag_id, new_name)
            if error:
                return render_template(
                    "tag_rename.html",
                    page="tags",
                    page_title="Rename Tag",
                    tag=tag,
                    form_name=new_name,
                    error=error,
                ), 400
            flash("Tag renamed.", "success")
            return redirect(url_for("tags"))
        return render_template(
            "tag_rename.html",
            page="tags",
            page_title="Rename Tag",
            tag=tag,
            form_name=tag["name"],
            error=None,
        )

    @app.post("/tags/<int:tag_id>/delete")
    def delete_tag(tag_id: int):
        conn = db.get_db()
        if bm.get_tag(conn, tag_id) is None:
            abort(404)
        bm.delete_tag(conn, tag_id)
        flash("Tag deleted.", "success")
        return redirect(url_for("tags"))

    # ── Duplicates ────────────────────────────────────────────────────────────

    @app.get("/duplicates")
    def duplicates():
        conn = db.get_db()
        sort = request.args.get("sort", "url")
        if sort not in {"url", "size"}:
            sort = "url"
        groups = bm.find_duplicate_groups(conn, sort=sort)
        return render_template(
            "duplicates.html",
            page="duplicates",
            page_title="Duplicates",
            groups=groups,
            sort=sort,
        )

    @app.post("/duplicates/<int:bookmark_id>/delete")
    def delete_duplicate(bookmark_id: int):
        conn = db.get_db()
        bookmark = bm.get_bookmark(conn, bookmark_id)
        if bookmark is None:
            abort(404)
        # Safety: block deletion if this is the last bookmark with this URL.
        # The duplicate review area must never silently remove the final copy.
        if bm.count_bookmarks_with_url(conn, bookmark["url"]) <= 1:
            flash(
                "This is the only remaining bookmark with this URL. "
                "Open it in the edit view to delete it directly.",
                "error",
            )
            return redirect(url_for("duplicates"))
        bm.delete_bookmark(conn, bookmark_id)
        flash("Bookmark deleted.", "success")
        return redirect(url_for("duplicates"))


def _is_filtered(params: dict) -> bool:
    """Return True if the user has applied a search or filter to the current view.

    Sort and the page-identity 'favorites_only' flag are intentionally excluded —
    they don't change the scope, only its presentation or its base set.
    """
    return bool(
        params.get("query")
        or params.get("unsorted_only")
        or params.get("collection_id")
        or params.get("tag_id")
    )


def _parse_list_params(args) -> dict:
    def maybe_int(v):
        try:
            return int(v) if v not in (None, "") else None
        except ValueError:
            return None

    sort = args.get("sort", "newest")
    if sort not in {"newest", "oldest", "title"}:
        sort = "newest"

    return {
        "favorites_only": False,
        "unsorted_only": args.get("filter") == "unsorted",
        "collection_id": maybe_int(args.get("collection")),
        "tag_id": maybe_int(args.get("tag")),
        "query": (args.get("q") or "").strip(),
        "sort": sort,
    }


def _parse_form(form) -> tuple[dict, dict]:
    url = (form.get("url") or "").strip()
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    is_favorite = form.get("is_favorite") in ("on", "1", "true")

    collection_ids: list[int] = []
    for raw in form.getlist("collection_ids"):
        try:
            collection_ids.append(int(raw))
        except ValueError:
            continue

    new_collection_names = bm.split_tag_input(form.get("new_collections", ""))
    tag_names = bm.split_tag_input(form.get("tags", ""))

    errors: dict[str, str] = {}
    if not url:
        errors["url"] = "URL is required."
    elif not (url.startswith("http://") or url.startswith("https://")):
        errors["url"] = "URL must start with http:// or https://."

    return (
        {
            "url": url,
            "title": title,
            "description": description,
            "is_favorite": is_favorite,
            "collection_ids": collection_ids,
            "new_collection_names": new_collection_names,
            "tag_names": tag_names,
        },
        errors,
    )


if __name__ == "__main__":
    create_app().run(debug=True)
