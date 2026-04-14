

from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime
import random
import string
from ..models.order_model import Order, OrderItem
from ..models.cart_model import Cart
from ..models.food_model import FoodItem


class OrderService:
    
    @staticmethod
    def _generate_order_number() -> str:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{timestamp}-{random_suffix}"
    
    @staticmethod
    def _validate_order_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:

        errors = []
        
        required_fields = ['customer_name', 'customer_email', 'customer_phone']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        if data.get('customer_email') and '@' not in data['customer_email']:
            errors.append("Invalid email address")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_all_orders(include_inactive=False) -> List[Order]:
       
        queryset = Order.objects.select_related().prefetch_related('order_items__food_item')
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        return list(queryset)
    
    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Order]:
       
        try:
            return Order.objects.select_related().prefetch_related(
                'order_items__food_item'
            ).get(id=order_id, is_active=True)
        except Order.DoesNotExist:
            return None
    
    @staticmethod
    def get_order_by_number(order_number: str) -> Optional[Order]:
        
        try:
            return Order.objects.select_related().prefetch_related(
                'order_items__food_item'
            ).get(order_number=order_number, is_active=True)
        except Order.DoesNotExist:
            return None
    
    @staticmethod
    def get_orders_by_customer_email(email: str) -> List[Order]:
        
        return list(Order.objects.select_related().prefetch_related(
            'order_items__food_item'
        ).filter(
            customer_email__iexact=email,
            is_active=True
        ).order_by('-created_at'))
    


    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart: Cart, order_data: Dict[str, Any]) -> Optional[Order]:
        
        is_valid, errors = OrderService._validate_order_data(order_data)
        if not is_valid:
            return None
        
        if cart.is_empty():
            return None
    
        for item in cart.cart_items.all():
            if not item.food_item.is_available:
                return None
        
       
        order_type = order_data.get('order_type', Order.OrderType.BASIC)
        
        # Create order
        order = Order(
            order_number=OrderService._generate_order_number(),
            customer_name=order_data['customer_name'],
            customer_email=order_data['customer_email'],
            customer_phone=order_data['customer_phone'],
            delivery_address=order_data.get('delivery_address', ''),
            special_instructions=order_data.get('special_instructions', ''),
            order_type=order_type,
            status=Order.OrderStatus.PENDING,
            payment_method=order_data.get('payment_method', ''),
            payment_status=order_data.get('payment_status', 'PENDING'),
            delivery_notes=order_data.get('delivery_notes', ''),
            estimated_delivery_time=order_data.get('estimated_delivery_time', 45),
        )
        
        if not order.validate():
            return None
        
        order.save()
        

        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                food_item=cart_item.food_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.food_item.price
            )

        order.total_amount = order.calculate_total()
        order.save(update_fields=['total_amount'])
        

        cart.clear_cart()
        
        return order

    @staticmethod
    @transaction.atomic
    def create_order_with_items(
        order_data: Dict[str, Any],
        items: List[Dict[str, Any]],
    ) -> tuple[Optional[Order], List[str]]:
        errors: List[str] = []

        is_valid, validation_errors = OrderService._validate_order_data(order_data)
        if not is_valid:
            errors.extend(validation_errors)

        if not items:
            errors.append("Order items are required")

        prepared_items: List[tuple[FoodItem, int]] = []
        if items:
            for item in items:
                if not isinstance(item, dict):
                    errors.append("Each item must be an object")
                    continue

                food_item_id = item.get("food_item_id")
                quantity = item.get("quantity", 1)

                try:
                    food_item_id = int(food_item_id)
                except (TypeError, ValueError):
                    errors.append("Invalid food_item_id")
                    continue

                try:
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    errors.append(f"Invalid quantity for item {food_item_id}")
                    continue

                if quantity < 1:
                    errors.append(f"Quantity must be at least 1 for item {food_item_id}")
                    continue

                try:
                    food_item = FoodItem.objects.get(id=food_item_id, is_active=True)
                except FoodItem.DoesNotExist:
                    errors.append(f"Food item {food_item_id} not found")
                    continue

                if not food_item.is_available:
                    errors.append(f"{food_item.name} is not available")
                    continue

                prepared_items.append((food_item, quantity))

        if errors:
            return None, errors

        order_type = order_data.get("order_type") or Order.OrderType.BASIC
        order = Order(
            order_number=OrderService._generate_order_number(),
            customer_name=order_data["customer_name"],
            customer_email=order_data["customer_email"],
            customer_phone=order_data["customer_phone"],
            delivery_address=order_data.get("delivery_address", ""),
            special_instructions=order_data.get("special_instructions", ""),
            order_type=order_type,
            status=Order.OrderStatus.PENDING,
            payment_method=order_data.get("payment_method", ""),
            payment_status=order_data.get("payment_status", "PENDING"),
            delivery_notes=order_data.get("delivery_notes", ""),
            estimated_delivery_time=order_data.get("estimated_delivery_time", 45),
        )

        if not order.validate():
            return None, order._get_validation_errors()

        order.save()

        for food_item, quantity in prepared_items:
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                unit_price=food_item.price,
            )

        order.total_amount = order.calculate_total()
        order.save(update_fields=["total_amount"])

        return order, []
    
    @staticmethod
    def update_order_status(order_id: int, new_status: str) -> Optional[Order]:
        
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return None
        
   
        valid_statuses = [choice[0] for choice in Order.OrderStatus.choices]
        if new_status not in valid_statuses:
            return None
        
        order.update_status(new_status)
        return order
    
    @staticmethod
    def cancel_order(order_id: int) -> Optional[Order]:
       
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return None
        
        if not order.can_cancel():
            return None
        
        order.update_status(Order.OrderStatus.CANCELLED)
        return order
    
    @staticmethod
    def get_orders_by_status(status: str) -> List[Order]:
      
        return list(Order.objects.select_related().prefetch_related(
            'order_items__food_item'
        ).filter(
            status=status,
            is_active=True
        ).order_by('-created_at'))
    
    @staticmethod
    def get_recent_orders(limit: int = 10) -> List[Order]:
     
        return list(Order.objects.select_related().prefetch_related(
            'order_items__food_item'
        ).filter(
            is_active=True
        ).order_by('-created_at')[:limit])
    

    
    @staticmethod
    def get_order_statistics() -> Dict[str, Any]:
       
        total_orders = Order.objects.filter(is_active=True).count()
        pending_orders = Order.objects.filter(
            status=Order.OrderStatus.PENDING,
            is_active=True
        ).count()
        completed_orders = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED,
            is_active=True
        ).count()
        cancelled_orders = Order.objects.filter(
            status=Order.OrderStatus.CANCELLED,
            is_active=True
        ).count()
        
        total_revenue = Order.objects.filter(
            status=Order.OrderStatus.DELIVERED,
            is_active=True
        ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue
        }
