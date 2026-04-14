

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from ..services.food_service import FoodService
from ..models.food_model import FoodItem


class FoodController:
    @staticmethod
    def index(request):
    
        category = request.GET.get('category')
        search_query = request.GET.get('search', '')
        

        if search_query:
            food_items = FoodService.search_food_items(search_query)
        elif category:
            food_items = FoodService.get_food_items_by_category(category)
        else:
            food_items = FoodService.get_available_food_items()
        
        categories = FoodService.get_menu_categories()
        
        context = {
            'food_items': food_items,
            'categories': categories,
            'selected_category': category,
            'search_query': search_query,
        }
        
        return render(request, 'foodapp/menu.html', context)
    
    @staticmethod
    def show(request, food_id):
       
        food_item = FoodService.get_food_item_by_id(food_id)
        
        if not food_item:
            messages.error(request, 'Food item not found')
            return redirect('menu')
        
        context = {
            'food_item': food_item,
        }
        
        return render(request, 'foodapp/food_detail.html', context)
    
    @staticmethod
    @require_http_methods(["GET"])
    def create(request):
        categories = FoodItem.Category.choices
        
        context = {
            'categories': categories,
            'action': 'Create',
        }
        
        return render(request, 'foodapp/food_form.html', context)
    
    @staticmethod
    @require_http_methods(["POST"])
    def store(request):
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description', ''),
            'price': request.POST.get('price'),
            'category': request.POST.get('category', FoodItem.Category.MAIN_COURSE),
            'is_available': request.POST.get('is_available') == 'on',
            'image': request.FILES.get('image'),
        }
        
        try:
            food_item = FoodService.create_food_item(data)
            messages.success(request, f'{food_item.name} created successfully!')
            return redirect('food_detail', food_id=food_item.id)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating food item: {str(e)}')

        return redirect('food_create')

    @staticmethod
    @require_http_methods(["GET"])
    def edit(request, food_id):
       
        food_item = FoodService.get_food_item_by_id(food_id)
        
        if not food_item:
            messages.error(request, 'Food item not found')
            return redirect('menu')
        
        categories = FoodItem.Category.choices
        
        context = {
            'food_item': food_item,
            'categories': categories,
            'action': 'Edit',
        }
        
        return render(request, 'foodapp/food_form.html', context)
    
    @staticmethod
    @require_http_methods(["POST"])
    def update(request, food_id):
        data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description', ''),
            'price': request.POST.get('price'),
            'category': request.POST.get('category'),
            'is_available': request.POST.get('is_available') == 'on',
        }
        
        updated_item = FoodService.update_food_item(food_id, data)
        
        if updated_item:
            messages.success(request, f'{updated_item.name} updated successfully!')
            return redirect('food_detail', food_id=updated_item.id)
        
        messages.error(request, 'Error updating food item')
        return redirect('food_edit', food_id=food_id)

    @staticmethod
    @require_http_methods(["POST"])
    def destroy(request, food_id):
        
        success = FoodService.delete_food_item(food_id, soft_delete=True)
        
        if success:
            messages.success(request, 'Food item deleted successfully!')
        else:
            messages.error(request, 'Error deleting food item')
        
        return redirect('menu')
    
    @staticmethod
    @require_http_methods(["POST"])
    def toggle_availability(request, food_id):
        
        food_item = FoodService.toggle_availability(food_id)
        
        if food_item:
            status = "available" if food_item.is_available else "unavailable"
            return JsonResponse({
                'success': True,
                'message': f'{food_item.name} is now {status}',
                'is_available': food_item.is_available
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Food item not found'
        }, status=404)
    
