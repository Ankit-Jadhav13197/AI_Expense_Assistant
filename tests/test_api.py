# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.db.session import engine
from api.db import models
import datetime

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # create tables fresh for tests (careful: in prod don't drop)
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

def test_create_and_get_expense():
    payload = {
        "date": datetime.date.today().isoformat(),
        "description": "Test coffee",
        "amount": 3.5,
        "category": "Food"
    }
    r = client.post("/expenses/", json=payload)
    assert r.status_code == 201
    created = r.json()
    exp_id = created["id"]

    r2 = client.get(f"/expenses/{exp_id}")
    assert r2.status_code == 200
    assert r2.json()["description"] == "Test coffee"

def test_list_and_delete():
    # create second
    payload = {"date": datetime.date.today().isoformat(), "description": "Taxi", "amount": 7.0}
    r = client.post("/expenses/", json=payload)
    assert r.status_code == 201

    rlist = client.get("/expenses/")
    assert rlist.status_code == 200
    assert len(rlist.json()) >= 1

    # delete first item
    first_id = rlist.json()[0]["id"]
    rdel = client.delete(f"/expenses/{first_id}")
    assert rdel.status_code == 204
