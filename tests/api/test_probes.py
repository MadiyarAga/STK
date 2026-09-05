from unittest import mock

import pytest
from django.db import OperationalError
from django.db.backends.base.base import BaseDatabaseWrapper


@pytest.fixture
def broken_database():
    with mock.patch.object(
        BaseDatabaseWrapper,
        'cursor',
        side_effect=OperationalError('база недоступна'),
    ):
        yield


def test_health_is_200_without_database(client, broken_database):
    assert client.get('/api/v1/health').status_code == 200


def test_ready_is_503_without_database(client, broken_database):
    assert client.get('/api/v1/ready').status_code == 503
