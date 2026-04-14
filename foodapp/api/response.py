from typing import Any, Dict, Optional
from django.http import JsonResponse


def success_response(
    data: Optional[Any] = None,
    message: str = "OK",
    status: int = 200,
) -> JsonResponse:
    payload: Dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return JsonResponse(payload, status=status)


def error_response(
    message: str,
    status: int = 400,
    errors: Optional[Any] = None,
) -> JsonResponse:
    payload: Dict[str, Any] = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return JsonResponse(payload, status=status)
