from typing import Dict, Any
from ..models.food_model import FoodItem
from ..models.order_model import Order, OrderItem


def serialize_food_item(item: FoodItem) -> Dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": float(item.price),
        "category": item.category,
        "category_display": item.get_category_display(),
        "food_type": item.food_type,
        "is_available": item.is_available,
    }


def serialize_order_item(item: OrderItem) -> Dict[str, Any]:
    return {
        "id": item.id,
        "food_item": {
            "id": item.food_item.id,
            "name": item.food_item.name,
            "price": float(item.unit_price),
        },
        "quantity": item.quantity,
        "subtotal": float(item.calculate_subtotal()),
    }


def serialize_order(order: Order) -> Dict[str, Any]:
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "status": order.status,
        "status_display": order.get_status_display(),
        "order_type": order.order_type,
        "total_amount": float(order.total_amount),
        "total_items": order.get_total_items(),
        "created_at": order.created_at.isoformat(),
        "items": [serialize_order_item(item) for item in order.order_items.all()],
    }
