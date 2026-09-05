def test_request_id_header_present_on_success(client):
    assert client.get('/api/v1/health').headers['X-Request-Id']


def test_request_id_header_matches_body(client):
    response = client.post('/api/v1/health')

    assert response.headers['X-Request-Id'] == response.json()['request_id']


def test_incoming_request_id_is_reused(client):
    response = client.get('/api/v1/health', headers={'X-Request-Id': 'trace-123'})

    assert response.headers['X-Request-Id'] == 'trace-123'
