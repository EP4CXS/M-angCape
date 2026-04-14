

from django.db import transaction
from typing import Optional, Dict, Any, List
from decimal import Decimal
from ..models.cart_model import Cart, CartItem
from ..models.food_model import FoodItem


class CartService:
    @staticmethod
    def _validate_cart_item(quantity: int, food_item: FoodItem) -> tuple[bool, str]:
        if quantity < 1:
            return False, "Quantity must be at least 1"
        
        if not food_item.is_available:
            return False, f"{food_item.name} is not available"
        
        if not food_item.is_active:
            return False, f"{food_item.name} no longer exists"
        
        return True, ""
    
    @staticmethod
    def get_or_create_cart(session_key: Optional[str] = None) -> Cart:
        if session_key:
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                is_active=True,
                defaults={'session_key': session_key}
            )
            return cart
        

        cart = Cart.objects.create(is_active=True)
        return cart
    
    @staticmethod
    def get_cart_by_session(session_key: str) -> Optional[Cart]:

        try:
            return Cart.objects.prefetch_related(
                'cart_items__food_item'
            ).get(session_key=session_key, is_active=True)
        except Cart.DoesNotExist:
            return None
    
    @staticmethod
    def get_cart_by_id(cart_id: int) -> Optional[Cart]:  
        try:
            return Cart.objects.prefetch_related(
                'cart_items__food_item'
            ).get(id=cart_id, is_active=True)
        except Cart.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def add_item_to_cart(cart: Cart, food_item_id: int, quantity: int = 1, notes: str = "") -> tuple[bool, str]:
    
        try:
            food_item = FoodItem.objects.get(id=food_item_id, is_active=True)
        except FoodItem.DoesNotExist:
            return False, "Food item not found"
        
        is_valid, error_message = CartService._validate_cart_item(quantity, food_item)
        if not is_valid:
            return False, error_message
   
        existing_item = CartItem.objects.filter(
            cart=cart,
            food_item=food_item
        ).first()
        
        if existing_item:
   
            existing_item.quantity += quantity
            existing_item.save(update_fields=['quantity'])
            return True, f"Updated {food_item.name} quantity in cart"
        

        CartItem.objects.create(
            cart=cart,
            food_item=food_item,
            quantity=quantity,
            notes=notes
        )
        
        return True, f"Added {food_item.name} to cart"
    

    @staticmethod
    @transaction.atomic
    def update_item_quantity(cart: Cart, item_id: int, quantity: int) -> tuple[bool, str]:
    
        if quantity < 1:
            return CartService.remove_item_from_cart(cart, item_id)
        
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )
        except CartItem.DoesNotExist:
            return False, "Item not found in cart"
        
        if not cart_item.food_item.is_available:
            return False, f"{cart_item.food_item.name} is no longer available"
        
        cart_item.quantity = quantity
        cart_item.save(update_fields=['quantity'])
        
        return True, "Quantity updated"
    

    @staticmethod
    @transaction.atomic
    def remove_item_from_cart(cart: Cart, item_id: int) -> tuple[bool, str]:
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )
        except CartItem.DoesNotExist:
            return False, "Item not found in cart"
        
        cart_item.delete()
        return True, "Item removed from cart"
    

    @staticmethod
    @transaction.atomic
    def clear_cart(cart: Cart) -> bool:
        cart.clear_cart()
        return True
    
    @staticmethod
    def get_cart_summary(cart: Cart) -> Dict[str, Any]:

        cart_items = cart.cart_items.all()
        
        items = []
        for item in cart_items:
            items.append({
                'id': item.id,
                'food_item': {
                    'id': item.food_item.id,
                    'name': item.food_item.name,
                    'price': float(item.food_item.price),
                },
                'quantity': item.quantity,
                'subtotal': float(item.get_subtotal()),
                'notes': item.notes
            })
        
        return {
            'cart_id': cart.id,
            'item_count': cart.get_item_count(),
            'items': items,
            'subtotal': float(cart.get_subtotal()),
            'tax': float(cart.get_tax()),
            'total': float(cart.get_total()),
            'is_empty': cart.is_empty()
        }
    
    @staticmethod
    def validate_cart(cart: Cart) -> tuple[bool, List[str]]:
       
        errors = []
        
        if cart.is_empty():
            errors.append("Cart is empty")
            return False, errors
        
        
        for item in cart.cart_items.all():
            if not item.food_item.is_available:
                errors.append(f"{item.food_item.name} is no longer available")
        
       
        return len(errors) == 0, errors
    
    @staticmethod
    def get_cart_item_count(session_key: str) -> int:
      
        cart = CartService.get_cart_by_session(session_key)
        if cart:
            return cart.get_item_count()
        return 0
