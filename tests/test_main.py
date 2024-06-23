import pytest
from app.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_object(client):
    rv = client.post('/create_object', json={'object_name': 'test_object'}, headers={'user_id': '123'})
    assert rv.status_code == 200
    assert b'Object test_object created for user 123' in rv.data
