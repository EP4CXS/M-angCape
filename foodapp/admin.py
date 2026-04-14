

from django.contrib import admin
from .models.food_model import FoodItem
from .models.order_model import Order, OrderItem
from .models.cart_model import Cart, CartItem


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    """Admin configuration for FoodItem model."""
    list_display = ('name', 'category', 'price', 'food_type', 'is_available', 'is_active')
    list_filter = ('category', 'food_type', 'is_available', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_available', 'is_active')
    ordering = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    list_display = ('id', 'customer_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'id')
    list_editable = ('status',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""
    list_display = ('order', 'food_item', 'quantity', 'unit_price')
    search_fields = ('order__id', 'food_item__name')
    ordering = ('order',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    list_display = ('id', 'customer_name', 'customer_email', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'session_key')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model."""
    list_display = ('cart', 'food_item', 'quantity', 'notes')
    search_fields = ('cart__id', 'food_item__name')
    ordering = ('cart',)
