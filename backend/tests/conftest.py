import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "pm.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))
    with TestClient(app) as test_client:
        yield test_client
