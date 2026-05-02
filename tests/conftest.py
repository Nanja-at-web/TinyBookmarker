import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402

# Fixed token used by the test client wrapper.
TEST_CSRF_TOKEN = "test-csrf-token"


class CsrfTestClient:
    """Wraps the Flask test client to automatically inject the CSRF token into
    every POST request.  This keeps existing tests unchanged while still
    exercising the real CSRF-protected routes."""

    def __init__(self, flask_client):
        self._client = flask_client
        with flask_client.session_transaction() as sess:
            sess["csrf_token"] = TEST_CSRF_TOKEN

    def post(self, *args, data=None, **kwargs):
        if data is None:
            data = {}
        if isinstance(data, dict) and "csrf_token" not in data:
            data = {**data, "csrf_token": TEST_CSRF_TOKEN}
        return self._client.post(*args, data=data, **kwargs)

    def __getattr__(self, name):
        return getattr(self._client, name)


@pytest.fixture
def app():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    application = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    yield application
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    return CsrfTestClient(app.test_client())
