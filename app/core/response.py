from typing import Any


def api_response(message: str, data: Any) -> dict:
    return {"message": message, "data": data}
