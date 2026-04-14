from django.views.decorators.csrf import csrf_exempt
from ..api.request import (
    parse_json_body,
    validate_food_payload,
    validate_order_payload,
    validate_food_update_payload,
    validate_order_update_payload,
)
from ..api.response import success_response, error_response
from ..api.serializers import serialize_food_item, serialize_order
from ..services.food_service import FoodService
from ..services.order_service import OrderService


class ApiFoodController:
    @staticmethod
    @csrf_exempt
    def collection(request):
        if request.method == "GET":
            return ApiFoodController.index(request)
        if request.method == "POST":
            return ApiFoodController.store(request)
        return error_response("Method not allowed", status=405)

    @staticmethod
    @csrf_exempt
    def member(request, food_id):
        if request.method == "GET":
            return ApiFoodController.show(request, food_id)
        if request.method in ["PUT", "PATCH"]:
            return ApiFoodController.update(request, food_id)
        if request.method == "DELETE":
            return ApiFoodController.destroy(request, food_id)
        return error_response("Method not allowed", status=405)

    @staticmethod
    def index(request):
        category = request.GET.get("category")
        if category:
            food_items = FoodService.get_food_items_by_category(category)
        else:
            food_items = FoodService.get_available_food_items()
        return success_response(
            {"foods": [serialize_food_item(item) for item in food_items]}
        )

    @staticmethod
    def show(request, food_id):
        food_item = FoodService.get_food_item_by_id(food_id)
        if not food_item:
            return error_response("Food item not found", status=404)
        return success_response({"food": serialize_food_item(food_item)})

    @staticmethod
    def store(request):
        ok, payload, errors = parse_json_body(request)
        if not ok:
            return error_response("Invalid request body", errors=errors)

        is_valid, data, validation_errors = validate_food_payload(payload)
        if not is_valid:
            return error_response("Validation failed", errors=validation_errors)

        try:
            food_item = FoodService.create_food_item(data)
        except ValueError as exc:
            return error_response("Validation failed", errors=[str(exc)])
        except Exception as exc:
            return error_response("Unable to create food item", status=500, errors=[str(exc)])

        return success_response(
            {"food": serialize_food_item(food_item)},
            message="Food item created",
            status=201,
        )

    @staticmethod
    def update(request, food_id):
        ok, payload, errors = parse_json_body(request)
        if not ok:
            return error_response("Invalid request body", errors=errors)

        is_valid, data, validation_errors = validate_food_update_payload(payload)
        if not is_valid:
            return error_response("Validation failed", errors=validation_errors)

        updated_item = FoodService.update_food_item(food_id, data)
        if not updated_item:
            return error_response("Food item not found or invalid", status=404)

        return success_response(
            {"food": serialize_food_item(updated_item)},
            message="Food item updated",
        )

    @staticmethod
    def destroy(request, food_id):
        success = FoodService.delete_food_item(food_id, soft_delete=True)
        if not success:
            return error_response("Food item not found", status=404)
        return success_response(message="Food item deleted")


class ApiOrderController:
    @staticmethod
    @csrf_exempt
    def collection(request):
        if request.method == "GET":
            return ApiOrderController.index(request)
        if request.method == "POST":
            return ApiOrderController.store(request)
        return error_response("Method not allowed", status=405)

    @staticmethod
    @csrf_exempt
    def member(request, order_id):
        if request.method == "GET":
            return ApiOrderController.show(request, order_id)
        if request.method in ["PUT", "PATCH"]:
            return ApiOrderController.update(request, order_id)
        if request.method == "DELETE":
            return ApiOrderController.destroy(request, order_id)
        return error_response("Method not allowed", status=405)

    @staticmethod
    def index(request):
        status = request.GET.get("status")
        email = request.GET.get("email")

        if status:
            orders = OrderService.get_orders_by_status(status)
        elif email:
            orders = OrderService.get_orders_by_customer_email(email)
        else:
            orders = OrderService.get_all_orders()

        return success_response({"orders": [serialize_order(order) for order in orders]})

    @staticmethod
    def show(request, order_id):
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return error_response("Order not found", status=404)
        return success_response({"order": serialize_order(order)})

    @staticmethod
    def store(request):
        ok, payload, errors = parse_json_body(request)
        if not ok:
            return error_response("Invalid request body", errors=errors)

        is_valid, order_data, items, validation_errors = validate_order_payload(payload)
        if not is_valid:
            return error_response("Validation failed", errors=validation_errors)

        order, create_errors = OrderService.create_order_with_items(order_data, items)
        if not order:
            return error_response("Unable to create order", errors=create_errors)

        return success_response(
            {"order": serialize_order(order)},
            message="Order created",
            status=201,
        )

    @staticmethod
    def update(request, order_id):
        ok, payload, errors = parse_json_body(request)
        if not ok:
            return error_response("Invalid request body", errors=errors)

        is_valid, update_data, validation_errors = validate_order_update_payload(payload)
        if not is_valid:
            return error_response("Validation failed", errors=validation_errors)

        new_status = update_data.get("status")
        if new_status:
            order = OrderService.update_order_status(order_id, new_status)
        else:
            order = None

        if not order:
            return error_response("Unable to update order", status=400)

        return success_response(
            {"order": serialize_order(order)},
            message="Order updated",
        )

    @staticmethod
    def destroy(request, order_id):
        order = OrderService.cancel_order(order_id)
        if not order:
            return error_response("Unable to cancel order", status=400)
        return success_response(
            {"order": serialize_order(order)},
            message="Order cancelled",
        )
