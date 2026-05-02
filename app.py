import hmac
import os
import secrets
from urllib.parse import urlencode

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import bookmarks as bm
import db


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    _secure_cookies = os.environ.get("TINYBOOKMARKER_SECURE_COOKIES", "").lower() in (
        "1", "true", "yes"
    )
    app.config.update(
        SECRET_KEY=os.environ.get("TINYBOOKMARKER_SECRET", "dev-secret-change-me"),
        DATABASE=os.environ.get(
            "TINYBOOKMARKER_DB",
            os.path.join(app.instance_path, "tinybookmarker.sqlite"),
        ),
        AUTH_PASSWORD=os.environ.get("TINYBOOKMARKER_PASSWORD", "").strip(),
        # Session cookie hardening.
        # HTTPONLY prevents JS access to the session cookie.
        # SAMESITE=Lax blocks cross-site POST (defence-in-depth alongside CSRF tokens).
        # SECURE must be enabled in production (HTTPS); leave off for plain-HTTP dev.
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_secure_cookies,
    )
    if config:
        app.config.update(config)

    db.init_db(app)
    db.init_app(app)

    app.jinja_env.globals["csrf_token"] = _get_csrf_token

    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.before_request
    def _check_csrf():
        if request.method == "POST":
            token = request.form.get("csrf_token", "")
            expected = session.get("csrf_token", "")
            if not expected or not hmac.compare_digest(token, expected):
                abort(403)

    @app.before_request
    def _check_auth():
        if not app.config.get("AUTH_PASSWORD"):
            return  # auth disabled — local dev or unconfigured
        if request.endpoint in ("login", "logout", "static"):
            return  # public endpoints
        if not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if not app.config.get("AUTH_PASSWORD"):
            return redirect(url_for("all_bookmarks"))
        if session.get("authenticated"):
            return redirect(url_for("all_bookmarks"))
        error = None
        if request.method == "POST":
            password = request.form.get("password", "")
            if hmac.compare_digest(password, app.config["AUTH_PASSWORD"]):
                session["authenticated"] = True
                next_url = request.form.get("next") or url_for("all_bookmarks")
                if not next_url.startswith("/"):
                    next_url = url_for("all_bookmarks")
                return redirect(next_url)
            error = "Wrong password."
        return render_template("login.html", error=error), (401 if error else 200)

    @app.post("/logout")
    def logout():
        session.pop("authenticated", None)
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.get("/")
    def index():
        return redirect(url_for("all_bookmarks"))

    @app.get("/bookmarks")
    def all_bookmarks():
        conn = db.get_db()
        params = _parse_list_params(request.args)
        page, per_page = _parse_pagination_params(request.args)
        items, total = bm.list_bookmarks(conn, **params, page=page, per_page=per_page)
        pagination = _build_pagination(request.args, total, page, per_page)
        return render_template(
            "bookmarks_list.html",
            page="all_bookmarks",
            page_title="All Bookmarks",
            page_subtitle="Your full bookmark library",
            items=items,
            pagination=pagination,
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
        page, per_page = _parse_pagination_params(request.args)
        items, total = bm.list_bookmarks(conn, **params, page=page, per_page=per_page)
        pagination = _build_pagination(request.args, total, page, per_page)
        return render_template(
            "bookmarks_list.html",
            page="favorites",
            page_title="Favorites",
            page_subtitle="Your personal quick-access bookmarks.",
            items=items,
            pagination=pagination,
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
        if sort not in {"name", "name_desc", "count", "count_asc"}:
            sort = "name"
        page, per_page = _parse_pagination_params(request.args)
        collections_list, total = bm.list_collections_with_counts(
            conn, sort=sort, page=page, per_page=per_page
        )
        pagination = _build_pagination(request.args, total, page, per_page)
        return render_template(
            "collections.html",
            page="collections",
            page_title="Collections",
            collections=collections_list,
            pagination=pagination,
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
            collections_list, total = bm.list_collections_with_counts(conn)
            pagination = _build_pagination({}, total, 1, bm.PAGE_SIZE_DEFAULT)
            return render_template(
                "collections.html",
                page="collections",
                page_title="Collections",
                collections=collections_list,
                pagination=pagination,
                sort="name",
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
        if sort not in {"name", "name_desc", "count", "count_asc"}:
            sort = "name"
        page, per_page = _parse_pagination_params(request.args)
        tags_list, total = bm.list_tags_with_counts(conn, sort=sort, page=page, per_page=per_page)
        pagination = _build_pagination(request.args, total, page, per_page)
        return render_template(
            "tags.html",
            page="tags",
            page_title="Tags",
            tags=tags_list,
            pagination=pagination,
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
        if sort not in {"url", "url_desc", "size", "size_asc"}:
            sort = "url"
        page, per_page = _parse_pagination_params(request.args)
        all_groups = bm.find_duplicate_groups(conn, sort=sort)
        total = len(all_groups)
        offset = (max(1, page) - 1) * per_page
        groups = all_groups[offset: offset + per_page]
        pagination = _build_pagination(request.args, total, page, per_page)
        return render_template(
            "duplicates.html",
            page="duplicates",
            page_title="Duplicates",
            groups=groups,
            pagination=pagination,
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
    if sort not in {"newest", "oldest", "title", "title_desc"}:
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


def _parse_pagination_params(args) -> tuple[int, int]:
    """Parse ?page= and ?per_page= from query args, with safe fallbacks."""
    try:
        page = max(1, int(args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = int(args.get("per_page", bm.PAGE_SIZE_DEFAULT))
        if per_page not in bm.PAGE_SIZES:
            per_page = bm.PAGE_SIZE_DEFAULT
    except (ValueError, TypeError):
        per_page = bm.PAGE_SIZE_DEFAULT
    return page, per_page


def _build_pagination(args, total: int, page: int, per_page: int) -> dict:
    """Return a dict with all data needed to render the pagination widget.

    Preserves every existing query-string key except 'page' and 'per_page'
    so filters and sort order are carried through when navigating pages.
    """
    num_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, num_pages))

    def _qs(**overrides) -> str:
        params = {k: v for k, v in args.items() if k not in ("page", "per_page")}
        params.update({k: str(v) for k, v in overrides.items()})
        return "?" + urlencode(params)

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "num_pages": num_pages,
        "has_prev": page > 1,
        "has_next": page < num_pages,
        "prev_url": _qs(page=page - 1, per_page=per_page) if page > 1 else None,
        "next_url": _qs(page=page + 1, per_page=per_page) if page < num_pages else None,
        "per_page_options": [
            {"value": pp, "url": _qs(page=1, per_page=pp), "selected": pp == per_page}
            for pp in bm.PAGE_SIZES
        ],
    }


def _get_csrf_token() -> str:
    """Return the per-session CSRF token, creating it on first call."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


if __name__ == "__main__":
    create_app().run(debug=True)
