

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from ..services.cart_service import CartService
from ..services.food_service import FoodService


class CartController:
    
    @staticmethod
    def _get_or_create_session_cart(request):
        session_key = request.session.session_key
        
        if not session_key:
           
            request.session.create()
            session_key = request.session.session_key
    
        cart = CartService.get_cart_by_session(session_key)
        
        if not cart:
            cart = CartService.get_or_create_cart(session_key)
        
    
        request.session['cart_id'] = cart.id
        
        return cart
    
    @staticmethod
    def index(request):
        cart_id = request.session.get('cart_id')
        
        if cart_id:
            cart = CartService.get_cart_by_id(cart_id)
        else:
            cart = None
        
        if not cart:
            cart = CartController._get_or_create_session_cart(request)
        
        summary = CartService.get_cart_summary(cart)
        
        context = {
            'cart': cart,
            'summary': summary,
        }
        
        return render(request, 'foodapp/cart.html', context)
    

    @staticmethod
    @require_http_methods(["POST"])
    
    def store(request):

        food_item_id = request.POST.get('food_item_id')
        quantity = int(request.POST.get('quantity', 1))
        notes = request.POST.get('notes', '')
        
        if not food_item_id:
            messages.error(request, 'Invalid food item')
            return redirect('menu')
        
        cart = CartController._get_or_create_session_cart(request)
        
        success, message = CartService.add_item_to_cart(
            cart, 
            int(food_item_id), 
            quantity, 
            notes
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            summary = CartService.get_cart_summary(cart)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_summary': summary
            })
        
        return redirect('cart')
    
    @staticmethod
    @require_http_methods(["POST"])
    def update(request, item_id):

        quantity = int(request.POST.get('quantity', 1))
        
        cart_id = request.session.get('cart_id')
        
        if not cart_id:
            messages.error(request, 'Cart not found')
            return redirect('menu')
        
        cart = CartService.get_cart_by_id(cart_id)
        
        if not cart:
            messages.error(request, 'Cart not found')
            return redirect('menu')
        
        success, message = CartService.update_item_quantity(cart, item_id, quantity)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            summary = CartService.get_cart_summary(cart)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_summary': summary
            })
        
        return redirect('cart')
    

    @staticmethod
    @require_http_methods(["POST"])
    def destroy(request, item_id):

        cart_id = request.session.get('cart_id')
        
        if not cart_id:
            messages.error(request, 'Cart not found')
            return redirect('menu')
        
        cart = CartService.get_cart_by_id(cart_id)
        
        if not cart:
            messages.error(request, 'Cart not found')
            return redirect('menu')
        
        success, message = CartService.remove_item_from_cart(cart, item_id)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            summary = CartService.get_cart_summary(cart)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_summary': summary
            })
        
        return redirect('cart')
    
    @staticmethod
    @require_http_methods(["POST"])
    def clear(request):

        cart_id = request.session.get('cart_id')
        
        if cart_id:
            cart = CartService.get_cart_by_id(cart_id)
            if cart:
                CartService.clear_cart(cart)
                messages.success(request, 'Cart cleared successfully')
        
        return redirect('cart')
    
    @staticmethod
    def summary(request):

        cart_id = request.session.get('cart_id')
        
        if cart_id:
            cart = CartService.get_cart_by_id(cart_id)
        else:
            cart = None
        
        if not cart:
            return JsonResponse({
                'item_count': 0,
                'total': 0,
                'is_empty': True
            })
        
        summary = CartService.get_cart_summary(cart)
        
        return JsonResponse(summary)
    
    @staticmethod
    def checkout(request):
        cart_id = request.session.get('cart_id')
        
        if not cart_id:
            messages.error(request, 'Your cart is empty')
            return redirect('menu')
        
        cart = CartService.get_cart_by_id(cart_id)
        
        if not cart or cart.is_empty():
            messages.error(request, 'Your cart is empty')
            return redirect('menu')
        
        is_valid, errors = CartService.validate_cart(cart)
        
        if not is_valid:
            for error in errors:
                messages.error(request, error)
            return redirect('cart')
        
        if request.method == 'POST':
            return redirect('order_create')
        
        summary = CartService.get_cart_summary(cart)
        
        context = {
            'cart': cart,
            'summary': summary,
        }
        
        return render(request, 'foodapp/checkout.html', context)
    

    @staticmethod
    @require_http_methods(["POST"])
    def quick_add(request, food_item_id):
        food_item = FoodService.get_food_item_by_id(food_item_id)
        
        if not food_item:
            return JsonResponse({
                'success': False,
                'message': 'Food item not found'
            }, status=404)
        
        if not food_item.is_available:
            return JsonResponse({
                'success': False,
                'message': 'This item is not available'
            }, status=400)
        
        cart = CartController._get_or_create_session_cart(request)
        
        success, message = CartService.add_item_to_cart(cart, food_item_id, 1)
        
        summary = CartService.get_cart_summary(cart)
        
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_summary': summary
        })
