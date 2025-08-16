import os
import sys
import importlib
from contextlib import contextmanager
from fastapi.testclient import TestClient
import pytest

# Ensure project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


@contextmanager
def app_with_origins(origins_list, use_alias=False):
    """
    Context manager that rebuilds the Pipeline Server app with given CORS origins.
    Uses JSON list string for reliable parsing by pydantic.
    """
    # Prepare environment
    json_list = str(origins_list).replace("'", '"')  # to JSON list
    env_key = 'PIPELINE_CORS_ORIGINS' if use_alias else 'CORS_ORIGINS'

    old_env = {k: os.environ.get(k) for k in ['PIPELINE_CORS_ORIGINS', 'CORS_ORIGINS']}
    try:
        # Set only one of them to validate alias behavior
        if use_alias:
            os.environ.pop('CORS_ORIGINS', None)
            os.environ[env_key] = json_list
        else:
            os.environ.pop('PIPELINE_CORS_ORIGINS', None)
            os.environ[env_key] = json_list

        # Reload settings and app modules
        for mod in [
            'app.pipelineserver.pipeline_app.main',
            'app.pipelineserver.pipeline_app.config',
        ]:
            if mod in sys.modules:
                del sys.modules[mod]
        config = importlib.import_module('app.pipelineserver.pipeline_app.config')
        importlib.reload(config)
        main = importlib.import_module('app.pipelineserver.pipeline_app.main')
        importlib.reload(main)
        yield main.app
    finally:
        # Restore environment
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _preflight(client: TestClient, origin: str, path: str = '/chat/azom'):
    return client.options(
        path,
        headers={
            'Origin': origin,
            'Access-Control-Request-Method': 'POST',
        },
    )


def test_preflight_allows_configured_origin():
    allowed = 'https://wp.example'
    with app_with_origins([allowed]) as app:
        with TestClient(app) as client:
            resp = _preflight(client, allowed)
            assert resp.status_code in (200, 204)
            assert resp.headers.get('access-control-allow-origin') == allowed
            assert resp.headers.get('access-control-allow-credentials') == 'true'


def test_preflight_blocks_unconfigured_origin():
    with app_with_origins(["https://a.example"]) as app:
        with TestClient(app) as client:
            resp = _preflight(client, 'https://b.example')
            assert resp.status_code in (200, 204)
            # No CORS headers for disallowed origin
            assert resp.headers.get('access-control-allow-origin') is None


def test_preflight_with_alias_env_var():
    allowed = 'https://alias.example'
    with app_with_origins([allowed], use_alias=True) as app:
        with TestClient(app) as client:
            resp = _preflight(client, allowed)
            assert resp.status_code in (200, 204)
            assert resp.headers.get('access-control-allow-origin') == allowed
