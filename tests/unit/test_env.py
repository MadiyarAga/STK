import pytest
from django.core.exceptions import ImproperlyConfigured

from stk_project.settings.env import env_bool, env_int, env_list, env_str

VAR = 'STK_TEST_VAR'
PURPOSE = 'тестовое назначение'

@pytest.fixture(autouse=True)
def _clean_var(monkeypatch):
    monkeypatch.delenv(VAR, raising=False)


@pytest.mark.parametrize('raw', ['YES', 'ON', 'TRUE', '1'])
def test_env_bool_accepts_truthy_in_any_case(monkeypatch, raw):
    monkeypatch.setenv(VAR, raw)
    assert env_bool(VAR, PURPOSE) is True


@pytest.mark.parametrize('raw', ['NO', 'OFF', 'FALSE', '0'])
def test_env_bool_accepts_falsy_in_any_case(monkeypatch, raw):
    monkeypatch.setenv(VAR, raw)
    assert env_bool(VAR, PURPOSE) is False


def test_env_bool_rejects_typo_instead_of_treating_it_as_false(monkeypatch):
    monkeypatch.setenv(VAR, 'ture')
    with pytest.raises(ImproperlyConfigured):
        env_bool(VAR, PURPOSE)


def test_env_int_rejects_non_numeric(monkeypatch):
    monkeypatch.setenv(VAR, '54x')

    with pytest.raises(ImproperlyConfigured):
        env_int(VAR, PURPOSE)


def test_env_list_trims_and_drops_empty_items(monkeypatch):
    monkeypatch.setenv(VAR, ' a , ,b,  ')

    assert env_list(VAR, PURPOSE) == ['a', 'b']


def test_env_list_rejects_value_of_separators_only(monkeypatch):
    monkeypatch.setenv(VAR, ',,,')

    with pytest.raises(ImproperlyConfigured):
        env_list(VAR, PURPOSE)


def test_whitespace_only_value_counts_as_missing(monkeypatch):
    monkeypatch.setenv(VAR, '   ')

    with pytest.raises(ImproperlyConfigured):
        env_str(VAR, PURPOSE)


def test_missing_variable_message_names_variable_and_purpose():
    with pytest.raises(ImproperlyConfigured) as excinfo:
        env_str(VAR, PURPOSE)

    assert VAR in str(excinfo.value)
    assert PURPOSE in str(excinfo.value)


@pytest.mark.parametrize(
    ('read_value', 'default'),
    [
        (env_str, 'строка'),
        (env_bool, 'no'),
        (env_int, 'не число'),
        (env_list, 'не список'),
    ],
)
def test_default_is_returned_untouched(read_value, default):
    assert read_value(VAR, PURPOSE, default=default) is default
