from .context import get_request_id


def build_error_body(code:str, message: str, details: list[dict] | None = None) -> dict:
    error = {'code': code, 'message': message}

    if details:
        error['details'] = details

    return {'error': error, 'request_id': get_request_id(),}
