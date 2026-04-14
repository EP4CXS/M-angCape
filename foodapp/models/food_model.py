

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .base_models import BaseModel


class FoodItem(BaseModel):
    
    class Category(models.TextChoices):
        APPETIZER = 'APPETIZER', 'Appetizer'
        MAIN_COURSE = 'MAIN_COURSE', 'Main Course'
        DESSERT = 'DESSERT', 'Dessert'
        DRINK = 'DRINK', 'Drink'
        SIDE_DISH = 'SIDE_DISH', 'Side Dish'
    
    # Additional fields for meal/drink types
    class FoodType(models.TextChoices):
        REGULAR = 'REGULAR', 'Regular'
        MEAL = 'MEAL', 'Meal'
        DRINK = 'DRINK', 'Drink'
    
    name = models.CharField(
        verbose_name='Food Name',
        max_length=200,
        unique=True,
        help_text='Name of the food item'
    )
    description = models.TextField(
        verbose_name='Description',
        blank=True,
        help_text='Description of the food item'
    )
    price = models.DecimalField(
        verbose_name='Price',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Price of the food item'
    )
    category = models.CharField(
        verbose_name='Category',
        max_length=20,
        choices=Category.choices,
        default=Category.MAIN_COURSE,
        help_text='Category of the food item'
    )
    food_type = models.CharField(
        verbose_name='Food Type',
        max_length=10,
        choices=FoodType.choices,
        default=FoodType.REGULAR,
        help_text='Type of food item'
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='food_images/',
        blank=True,
        null=True,
        help_text='Image of the food item'
    )
    is_available = models.BooleanField(
        verbose_name='Is Available',
        default=True,
        help_text='Whether the item is available for ordering'
    )
    
    # Meal-specific fields (optional)
    serving_size = models.PositiveIntegerField(
        verbose_name='Serving Size',
        default=1,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Number of servings'
    )
    preparation_time = models.PositiveIntegerField(
        verbose_name='Preparation Time (minutes)',
        default=30,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        help_text='Time to prepare in minutes'
    )
    is_vegetarian = models.BooleanField(
        verbose_name='Is Vegetarian',
        default=False,
        blank=True,
        help_text='Whether the meal is vegetarian'
    )
    calories = models.PositiveIntegerField(
        verbose_name='Calories',
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Calorie information'
    )
    
    # Drink-specific fields (optional)
    drink_size = models.CharField(
        verbose_name='Drink Size',
        max_length=10,
        blank=True,
        choices=[
            ('SMALL', 'Small'),
            ('MEDIUM', 'Medium'),
            ('LARGE', 'Large'),
        ],
        help_text='Size of the drink'
    )
    is_alcoholic = models.BooleanField(
        verbose_name='Is Alcoholic',
        default=False,
        blank=True,
        help_text='Whether the drink contains alcohol'
    )
    volume_ml = models.PositiveIntegerField(
        verbose_name='Volume (ml)',
        default=330,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Volume in milliliters'
    )
    
    # Private attribute for internal pricing logic
    _tax_rate = Decimal('0.10')  # 10% tax
    
    class Meta:
        verbose_name = 'Food Item'
        verbose_name_plural = 'Food Items'
        ordering = ['category', 'name']
    
    def get_display_name(self):
        """Return the display name for the food item."""
        return f"{self.name} - ₱{self.price}"
    
    def validate(self):
        """
        Validate the food item.
        Returns True if valid, False otherwise.
        """
        self._clear_validation_errors()
        
        if not self.name:
            self._set_validation_error("Food item must have a name")
        
        if self.price <= 0:
            self._set_validation_error("Price must be greater than 0")
        
        return not self.has_validation_errors()
    
    # Polymorphic method - can be overridden by child classes
    def calculate_price(self, quantity=1, apply_tax=True):
        total = self.price * Decimal(str(quantity))
        
        # Apply size-based pricing for drinks
        if self.food_type == self.FoodType.DRINK and self.drink_size:
            size_multiplier = {
                'SMALL': Decimal('0.75'),
                'MEDIUM': Decimal('1.00'),
                'LARGE': Decimal('1.50'),
            }
            total = total * size_multiplier.get(self.drink_size, Decimal('1.00'))
        
        # Apply bulk discount for meals
        if self.food_type == self.FoodType.MEAL and quantity >= 5:
            discount = total * Decimal('0.10')  # 10% bulk discount
            total = total - discount
        
        if apply_tax:
            total = self._apply_tax(total)
        
        return total
    
    # Encapsulated method for tax calculation
    def _apply_tax(self, amount):
        tax = amount * self._tax_rate
        return amount + tax
    
    def get_price_with_tax(self):
        """Get price including tax."""
        return self._apply_tax(self.price)
    
    def get_tax_amount(self):
        """Get the tax amount for this item."""
        return self.price * self._tax_rate
    
    def __str__(self):
        return self.name
