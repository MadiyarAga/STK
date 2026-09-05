from django.test import override_settings


@override_settings(DEBUG=False)
def test_unknown_route_returns_404(client):
    assert client.get('/api/v1/nosuchroute').status_code == 404


@override_settings(DEBUG=False)
def test_unknown_route_body_is_error_envelope(client):
    body = client.get('/api/v1/nosuchroute').json()

    assert body['error']['code'] == 'NOT_FOUND'
    assert body['error']['message']
    assert body['request_id']


def test_unsupported_method_returns_405(client):
    assert client.post('/api/v1/health').status_code == 405


def test_unsupported_method_body_is_error_envelope(client):
    body = client.post('/api/v1/health').json()

    assert body['error']['code'] == 'METHOD_NOT_ALLOWED'
    assert body['error']['message']
    assert body['request_id']
