from apps.core.exception_handler import _flatten, _headers_for


def test_list_index_goes_into_the_path():
    detail = {'items': [{'portions': ['Значение должно быть больше нуля']}]}

    assert _flatten(detail) == [
        {'field': 'items.0.portions', 'message': 'Значение должно быть больше нуля'},
    ]


def test_all_violations_are_reported_not_only_the_first():
    detail = {'name': ['Обязательное поле.'], 'price': ['Должно быть положительным.']}

    assert [entry['field'] for entry in _flatten(detail)] == ['name', 'price']


def test_valid_items_produce_no_entries():
    detail = {'items': [{}, {'portions': ['Ошибка.']}]}

    assert _flatten(detail) == [{'field': 'items.1.portions', 'message': 'Ошибка.'}]


def test_several_messages_for_one_field_do_not_get_an_index():
    detail = {'name': ['Слишком коротко.', 'Недопустимый символ.']}

    assert [entry['field'] for entry in _flatten(detail)] == ['name', 'name']


def test_error_without_a_field_has_field_none():
    assert _flatten('Общая ошибка.') == [{'field': None, 'message': 'Общая ошибка.'}]


def test_retry_after_is_rounded_up():
    class _ThrottledWithFractionalWait:
        wait = 0.4

    assert _headers_for(_ThrottledWithFractionalWait())['Retry-After'] == '1'


def test_auth_header_is_passed_through():
    class _Unauthenticated:
        auth_header = 'Bearer realm="api"'

    assert _headers_for(_Unauthenticated())['WWW-Authenticate'] == 'Bearer realm="api"'


def test_plain_exception_gets_no_extra_headers():
    assert _headers_for(ValueError('без спецполей')) == {}
