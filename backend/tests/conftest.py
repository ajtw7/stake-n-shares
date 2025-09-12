import pytest
import logging
import sys

@pytest.fixture(scope="session", autouse=True)
def _logging_setup():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
        stream=sys.stdout,
        force=True
    )

@pytest.fixture(autouse=True)
def disable_external_apis(monkeypatch):
    """
    Disable external API usage for deterministic unit tests.
    Integration tests explicitly re-enable.
    """
    try:
        from backend.app.config import settings
        monkeypatch.setattr(settings, "USE_EXTERNAL_APIS", False)
    except Exception:
        pass