"""
URL Configuration for Food App

This file defines all URL patterns for the food ordering system.
"""

from django.urls import path
from .controllers import food_controller, order_controller, cart_controller, api_controller

urlpatterns = [
    # Food URLs
    path('', food_controller.FoodController.index, name='home'),
    path('menu/', food_controller.FoodController.index, name='menu'),
    path('food/<int:food_id>/', food_controller.FoodController.show, name='food_detail'),
    path('food/create/', food_controller.FoodController.create, name='food_create'),
    path('food/store/', food_controller.FoodController.store, name='food_store'),
    path('food/<int:food_id>/edit/', food_controller.FoodController.edit, name='food_edit'),
    path('food/<int:food_id>/update/', food_controller.FoodController.update, name='food_update'),
    path('food/<int:food_id>/delete/', food_controller.FoodController.destroy, name='food_delete'),
    path('food/<int:food_id>/toggle/', food_controller.FoodController.toggle_availability, name='food_toggle'),
    
    # Order URLs
    path('orders/', order_controller.OrderController.index, name='order_list'),
    path('order/<int:order_id>/', order_controller.OrderController.show, name='order_detail'),
    path('order/create/', order_controller.OrderController.create, name='order_create'),
    path('order/store/', order_controller.OrderController.store, name='order_store'),
    path('order/<int:order_id>/confirmation/', order_controller.OrderController.confirmation, name='order_confirmation'),
    path('order/<int:order_id>/update-status/', order_controller.OrderController.update, name='order_update_status'),
    path('order/<int:order_id>/cancel/', order_controller.OrderController.destroy, name='order_cancel'),
    path('order/track/<str:order_number>/', order_controller.OrderController.track, name='order_track'),
    path('orders/statistics/', order_controller.OrderController.statistics, name='order_statistics'),
    
    # Cart URLs
    path('cart/', cart_controller.CartController.index, name='cart'),
    path('cart/add/', cart_controller.CartController.store, name='cart_add'),
    path('cart/<int:item_id>/update/', cart_controller.CartController.update, name='cart_update'),
    path('cart/<int:item_id>/remove/', cart_controller.CartController.destroy, name='cart_remove'),
    path('cart/clear/', cart_controller.CartController.clear, name='cart_clear'),
    path('cart/summary/', cart_controller.CartController.summary, name='cart_summary'),
    path('checkout/', cart_controller.CartController.checkout, name='checkout'),
    
    # Quick add to cart (AJAX)
    path('cart/quick-add/<int:food_item_id>/', cart_controller.CartController.quick_add, name='cart_quick_add'),
    
    # API URLs
    path('api/foods/', api_controller.ApiFoodController.collection, name='api_foods'),
    path('api/foods/<int:food_id>/', api_controller.ApiFoodController.member, name='api_food_detail'),
    path('api/orders/', api_controller.ApiOrderController.collection, name='api_orders'),
    path('api/orders/<int:order_id>/', api_controller.ApiOrderController.member, name='api_order_detail'),
]
