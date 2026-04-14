import json
from typing import Any, Dict, List, Tuple, Optional
from django.http import HttpRequest


def parse_json_body(request: HttpRequest) -> Tuple[bool, Dict[str, Any], List[str]]:
    if request.body:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return False, {}, ["Invalid JSON body"]
        if not isinstance(payload, dict):
            return False, {}, ["JSON body must be an object"]
        return True, payload, []

    if request.POST:
        return True, dict(request.POST), []

    if request.GET:
        return True, dict(request.GET), []

    return False, {}, ["Request body is required"]


def require_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    missing = []
    for field in required:
        value = data.get(field)
        if value is None or value == "":
            missing.append(field)
    return missing


def _coerce_bool(value: Any, field_name: str, errors: List[str], default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value_normalized = value.strip().lower()
        if value_normalized in ["true", "1", "yes", "y"]:
            return True
        if value_normalized in ["false", "0", "no", "n"]:
            return False
    errors.append(f"{field_name} must be a boolean")
    return default


def _coerce_int(value: Any, field_name: str, errors: List[str]) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        errors.append(f"{field_name} must be a number")
        return None


def _coerce_float(value: Any, field_name: str, errors: List[str]) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{field_name} must be a number")
        return None


def _unwrap_single(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def validate_food_payload(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    errors: List[str] = []
    normalized_payload = {
        key: _unwrap_single(value) for key, value in payload.items()
    }
    missing = require_fields(normalized_payload, ["name", "description", "price", "category"])
    if missing:
        errors.extend([f"{field} is required" for field in missing])

    price_value = _coerce_float(normalized_payload.get("price"), "price", errors)
    if price_value is not None and price_value <= 0:
        errors.append("price must be greater than 0")

    data = {
        "name": normalized_payload.get("name"),
        "description": normalized_payload.get("description", ""),
        "price": normalized_payload.get("price"),
        "category": normalized_payload.get("category"),
        "is_available": _coerce_bool(normalized_payload.get("is_available"), "is_available", errors, True),
    }

    return len(errors) == 0, data, errors


def validate_order_payload(
    payload: Dict[str, Any],
) -> Tuple[bool, Dict[str, Any], List[Dict[str, Any]], List[str]]:
    errors: List[str] = []
    normalized_payload = {
        key: _unwrap_single(value) for key, value in payload.items()
    }
    missing = require_fields(normalized_payload, ["customer_name", "customer_email", "customer_phone", "items"])
    if missing:
        errors.extend([f"{field} is required" for field in missing])

    items_raw = normalized_payload.get("items")
    items: List[Dict[str, Any]] = []
    if not isinstance(items_raw, list):
        errors.append("items must be an array")
    else:
        for index, item in enumerate(items_raw):
            if not isinstance(item, dict):
                errors.append(f"items[{index}] must be an object")
                continue

            food_item_id = _coerce_int(item.get("food_item_id"), f"items[{index}].food_item_id", errors)
            quantity = _coerce_int(item.get("quantity", 1), f"items[{index}].quantity", errors)

            if quantity is not None and quantity < 1:
                errors.append(f"items[{index}].quantity must be at least 1")

            if food_item_id is not None and quantity is not None:
                items.append({
                    "food_item_id": food_item_id,
                    "quantity": quantity,
                })

    data = {
        "customer_name": normalized_payload.get("customer_name"),
        "customer_email": normalized_payload.get("customer_email"),
        "customer_phone": normalized_payload.get("customer_phone"),
        "delivery_address": normalized_payload.get("delivery_address", ""),
        "special_instructions": normalized_payload.get("special_instructions", ""),
        "order_type": normalized_payload.get("order_type"),
        "payment_method": normalized_payload.get("payment_method", ""),
        "payment_status": normalized_payload.get("payment_status", "PENDING"),
        "delivery_notes": normalized_payload.get("delivery_notes", ""),
        "estimated_delivery_time": normalized_payload.get("estimated_delivery_time", 45),
    }

    return len(errors) == 0, data, items, errors


def validate_food_update_payload(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    errors: List[str] = []
    if not payload:
        return False, {}, ["Request body is required"]

    normalized_payload = {
        key: _unwrap_single(value) for key, value in payload.items()
    }
    data: Dict[str, Any] = {}
    if "name" in normalized_payload:
        data["name"] = normalized_payload.get("name")
    if "description" in normalized_payload:
        data["description"] = normalized_payload.get("description", "")
    if "price" in normalized_payload:
        price_value = _coerce_float(normalized_payload.get("price"), "price", errors)
        if price_value is not None and price_value <= 0:
            errors.append("price must be greater than 0")
        data["price"] = normalized_payload.get("price")
    if "category" in normalized_payload:
        data["category"] = normalized_payload.get("category")
    if "is_available" in normalized_payload:
        data["is_available"] = _coerce_bool(normalized_payload.get("is_available"), "is_available", errors, True)

    if not data:
        errors.append("No fields to update")

    return len(errors) == 0, data, errors


def validate_order_update_payload(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    errors: List[str] = []
    if not payload:
        return False, {}, ["Request body is required"]

    data: Dict[str, Any] = {}
    normalized_payload = {
        key: _unwrap_single(value) for key, value in payload.items()
    }
    if "status" in normalized_payload:
        data["status"] = normalized_payload.get("status")
    else:
        errors.append("status is required")

    return len(errors) == 0, data, errors
