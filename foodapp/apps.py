"""
FoodApp Configuration
"""

from django.apps import AppConfig


class FoodappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodapp'
    verbose_name = 'Food Ordering Application'
    
    def ready(self):
        """
        Initialize app when Django starts.
        """
        pass
