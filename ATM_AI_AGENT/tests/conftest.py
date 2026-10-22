from __future__ import annotations

import pytest

from atm_agent import banking


@pytest.fixture
def demo_db(tmp_path, monkeypatch):
    monkeypatch.setattr(banking, "DB_PATH", tmp_path / "atm-test.sqlite3")
    banking.seed_demo_account()
    return banking.DB_PATH
