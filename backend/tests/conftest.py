import pytest

@pytest.fixture(autouse=True)
def disable_external_apis(monkeypatch):
    """
    Disable external API usage for deterministic unit tests.
    """
    try:
        from backend.app.config import settings
        monkeypatch.setattr(settings, "USE_EXTERNAL_APIS", False)
        # print("Disabled external API usage for tests")
    except Exception:
        pass