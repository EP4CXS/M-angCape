
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from typing import Optional, Dict, Any
from ..services.order_service import OrderService
from ..models.order_model import Order


class OrderController:
    
    @staticmethod
    def index(request):

        status = request.GET.get('status')
        email = request.GET.get('email')
        
        if status:
            orders = OrderService.get_orders_by_status(status)
        elif email:
            orders = OrderService.get_orders_by_customer_email(email)
        else:
            orders = OrderService.get_all_orders()
        
        context = {
            'orders': orders,
            'selected_status': status,
            'email': email,
            'status_choices': Order.OrderStatus.choices,
        }
        
        return render(request, 'foodapp/order_list.html', context)
    
    @staticmethod
    def show(request, order_id):
        
        order = OrderService.get_order_by_id(order_id)
        
        if not order:
            messages.error(request, 'Order not found')
            return redirect('order_list')
        
        context = {
            'order': order,
        }
        
        return render(request, 'foodapp/order_detail.html', context)
    
    @staticmethod
    def create(request):
        context = {
            'order_statuses': Order.OrderStatus.choices,
        }
        
        return render(request, 'foodapp/order_form.html', context)
    
    @staticmethod
    def confirmation(request, order_id):
       
        order = OrderService.get_order_by_id(order_id)
        
        if not order:
            messages.error(request, 'Order not found')
            return redirect('order_list')
        
        context = {
            'order': order,
        }
        
        return render(request, 'foodapp/order_confirmation.html', context)
    
    @staticmethod
    @require_http_methods(["POST"])
    def update(request, order_id):

        new_status = request.POST.get('status')
        
        if not new_status:
            messages.error(request, 'Status is required')
            return redirect('order_detail', order_id=order_id)
        
        order = OrderService.update_order_status(order_id, new_status)
        
        if order:
            messages.success(request, f'Order #{order.order_number} status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Error updating order status')
        
        return redirect('order_detail', order_id=order_id)
    
    @staticmethod
    @require_http_methods(["POST"])
    def destroy(request, order_id):
        
        order = OrderService.cancel_order(order_id)
        
        if order:
            messages.success(request, f'Order #{order.order_number} has been cancelled')
        else:
            messages.error(request, 'Unable to cancel this order')
        
        return redirect('order_detail', order_id=order_id)
    
    @staticmethod
    def track(request, order_number):
        
        order = OrderService.get_order_by_number(order_number)
        
        if not order:
            messages.error(request, 'Order not found')
            return redirect('order_list')
        
        context = {
            'order': order,
        }
        
        return render(request, 'foodapp/order_track.html', context)


    @staticmethod
    def statistics(request):
    
        stats = OrderService.get_order_statistics()
        recent_orders = OrderService.get_recent_orders(10)
        
        context = {
            'stats': stats,
            'recent_orders': recent_orders,
        }
        
        return render(request, 'foodapp/order_statistics.html', context)

    @staticmethod
    @require_http_methods(["POST"])
    def store(request):
        data = {
            'customer_name': request.POST.get('customer_name'),
            'customer_email': request.POST.get('customer_email'),
            'customer_phone': request.POST.get('customer_phone'),
            'delivery_address': request.POST.get('delivery_address', ''),
            'special_instructions': request.POST.get('special_instructions', ''),
        }
        
        cart_id = request.session.get('cart_id')
        
        if not cart_id:
            messages.error(request, 'Your cart is empty')
            return redirect('cart')
        
        from ..services.cart_service import CartService
        cart = CartService.get_cart_by_id(cart_id)
        
        if not cart or cart.is_empty():
            messages.error(request, 'Your cart is empty')
            return redirect('cart')
        
        is_valid, errors = CartService.validate_cart(cart)
        if not is_valid:
            for error in errors:
                messages.error(request, error)
            return redirect('cart')
        
        order = OrderService.create_order_from_cart(cart, data)
        
        if order:
            request.session.pop('cart_id', None)
            messages.success(request, f'Order #{order.order_number} created successfully!')
            return redirect('order_confirmation', order_id=order.id)
        
        messages.error(request, 'Error creating order. Please try again.')
        return redirect('order_create')
