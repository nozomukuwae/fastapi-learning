from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from starlette import status
from ..database import Base
from ..main import app
from ..models import Todos
from ..routers.todos import get_db
from ..routers.auth import get_current_user

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'nozomu_test', 'user_id': 1, 'role': 'admin'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='todo1',
        description='todo1 description',
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'title': 'todo1',
        'description': 'todo1 description',
        'priority': 5,
        'complete': False,
        'owner_id': 1,
    }]


def test_read_todo_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'title': 'todo1',
        'description': 'todo1 description',
        'priority': 5,
        'complete': False,
        'owner_id': 1,
    }


def test_read_todo_authenticated_not_found(test_todo):
    response = client.get("/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}
