import time

import importlib


# Import AutoML module for testing
automl = importlib.import_module("mainappsrc.automl_core")


def test_load_user_data_parallel(monkeypatch):
    def fake_load_all_users():
        time.sleep(0.2)
        return {"u": "e"}

    def fake_load_user_config():
        time.sleep(0.2)
        return "name", "email"

    monkeypatch.setattr(automl, "load_all_users", fake_load_all_users)
    monkeypatch.setattr(automl, "load_user_config", fake_load_user_config)

    start = time.time()
    users, config = automl.load_user_data()
    elapsed = time.time() - start
    assert users == {"u": "e"}
    assert config == ("name", "email")
    assert elapsed < 0.35
