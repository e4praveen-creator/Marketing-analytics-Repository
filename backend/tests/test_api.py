from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200


def test_invalid_metric_400():
    r = client.post('/metrics/query', json={
        'metric': 'roi',
        'dimensions': ['campaign'],
        'filters': {},
        'date_range': {'start': '2024-01-01', 'end': '2030-01-01'}
    })
    assert r.status_code == 400


def test_chat_ctr():
    r = client.post('/chat/message', json={'message': 'CTR last 7 days'})
    assert r.status_code == 200
    body = r.json()
    assert 'answer' in body and body['tables']
