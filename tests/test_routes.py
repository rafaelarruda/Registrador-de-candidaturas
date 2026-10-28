from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models  # noqa: F401


@pytest.fixture
def client() -> Iterator[TestClient]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Iterator[Session]:
        with test_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_application(client: TestClient, **values: object) -> dict:
    payload = {"empresa": "Acme", "cargo": "Desenvolvedor", **values}
    response = client.post("/api/candidaturas", json=payload)
    assert response.status_code == 201
    return response.json()


def test_health_and_create_application(client: TestClient) -> None:
    page = client.get("/")
    assert page.status_code == 200
    assert "<title>Rastro | Candidaturas</title>" in page.text

    assert client.get("/health").json() == {"status": "ok"}

    created = create_application(
        client,
        empresa="  Acme  ",
        salario="  R$ 8.000 a combinar  ",
        requisitos="  Python e FastAPI\nPostgreSQL  ",
    )
    assert created["empresa"] == "Acme"
    assert created["salario"] == "R$ 8.000 a combinar"
    assert created["requisitos"] == "Python e FastAPI\nPostgreSQL"
    assert created["status"] == "enviado"
    assert client.get(f"/api/candidaturas/{created['id']}").json() == created


def test_list_applications_with_filters(client: TestClient) -> None:
    create_application(client, empresa="Acme", status="entrevista")
    create_application(client, empresa="Outra Empresa", status="enviado")

    response = client.get("/api/candidaturas", params={"status": "entrevista", "empresa": "acm"})

    assert response.status_code == 200
    assert response.headers["x-total-count"] == "1"
    assert [item["empresa"] for item in response.json()] == ["Acme"]


def test_update_and_delete_application(client: TestClient) -> None:
    created = create_application(client)

    updated = client.patch(
        f"/api/candidaturas/{created['id']}",
        json={
            "status": "oferta",
            "anotacoes": "Recebida",
            "salario": "R$ 10.000/mês",
            "requisitos": "Liderança técnica",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "oferta"
    assert updated.json()["anotacoes"] == "Recebida"
    assert updated.json()["salario"] == "R$ 10.000/mês"
    assert updated.json()["requisitos"] == "Liderança técnica"

    deleted = client.delete(f"/api/candidaturas/{created['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/candidaturas/{created['id']}").status_code == 404


def test_summary_and_validation(client: TestClient) -> None:
    create_application(client, status="entrevista")
    create_application(client, status="recusado")

    summary = client.get("/api/resumo").json()
    assert summary == {
        "total": 2,
        "por_status": {"enviado": 0, "entrevista": 1, "oferta": 0, "recusado": 1},
    }

    invalid = client.post(
        "/api/candidaturas", json={"empresa": "   ", "cargo": "Desenvolvedor"}
    )
    assert invalid.status_code == 422