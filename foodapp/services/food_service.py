

from django.db.models import Q
from decimal import Decimal
from typing import List, Optional, Dict, Any
from ..models.food_model import FoodItem


class FoodService:

    @staticmethod
    def get_all_food_items(include_inactive=False) -> List[FoodItem]:
      
        queryset = FoodItem.objects.all()
        if not include_inactive:
            queryset = queryset.filter(is_available=True)
        return list(queryset)
    
    @staticmethod
    def get_food_item_by_id(item_id: int) -> Optional[FoodItem]:
      
        try:
            return FoodItem.objects.get(id=item_id, is_active=True)
        except FoodItem.DoesNotExist:
            return None
    
    @staticmethod
    def search_food_items(query: str) -> List[FoodItem]:
     
        return list(FoodItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True,
            is_active=True
        ))
    
    @staticmethod
    def get_food_items_by_category(category: str) -> List[FoodItem]:
       
        return list(FoodItem.objects.filter(
            category=category,
            is_available=True,
            is_active=True
        ))
    
    @staticmethod
    def create_food_item(data: Dict[str, Any]) -> FoodItem:
       
        food_item = FoodItem(
            name=data.get('name'),
            description=data.get('description', ''),
            price=Decimal(str(data.get('price', 0))),
            category=data.get('category', FoodItem.Category.MAIN_COURSE),
            image=data.get('image'),
            is_available=data.get('is_available', True)
        )
        
        if food_item.validate():
            food_item.save()
            return food_item
        else:
            raise ValueError(f"Validation failed: {food_item._get_validation_errors()}")
    
    @staticmethod
    def update_food_item(item_id: int, data: Dict[str, Any]) -> Optional[FoodItem]:
      
        food_item = FoodService.get_food_item_by_id(item_id)
        if not food_item:
            return None
        
        if 'name' in data:
            food_item.name = data['name']
        if 'description' in data:
            food_item.description = data['description']
        if 'price' in data:
            food_item.price = Decimal(str(data['price']))
        if 'category' in data:
            food_item.category = data['category']
        if 'is_available' in data:
            food_item.is_available = data['is_available']
        if 'image' in data:
            food_item.image = data['image']
        
        if food_item.validate():
            food_item.save()
            return food_item
        
        return None
    
    @staticmethod
    def delete_food_item(item_id: int, soft_delete: bool = True) -> bool:
       
        food_item = FoodService.get_food_item_by_id(item_id)
        if not food_item:
            return False
        
        if soft_delete:
            food_item.soft_delete()
        else:
            food_item.delete()
        
        return True
    
    @staticmethod
    def get_menu_categories() -> List[Dict[str, str]]:
       
        categories = []
        for choice in FoodItem.Category.choices:
            categories.append({
                'value': choice[0],
                'label': choice[1],
                'count': FoodItem.objects.filter(
                    category=choice[0],
                    is_available=True,
                    is_active=True
                ).count()
            })
        return categories
    
    @staticmethod
    def get_available_food_items() -> List[FoodItem]:
       
        return list(FoodItem.objects.filter(
            is_available=True,
            is_active=True
        ).order_by('category', 'name'))
    
    @staticmethod
    def toggle_availability(item_id: int) -> Optional[FoodItem]:
       
        food_item = FoodService.get_food_item_by_id(item_id)
        if not food_item:
            return None
        
        food_item.is_available = not food_item.is_available
        food_item.save(update_fields=['is_available', 'updated_at'])
        return food_item
