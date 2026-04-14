

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base_models import BaseModel
from .food_model import FoodItem


class Cart(BaseModel):
    session_key = models.CharField(
        verbose_name='Session Key',
        max_length=40,
        blank=True,
        null=True,
        help_text='Session identifier for the cart'
    )
    customer_name = models.CharField(
        verbose_name='Customer Name',
        max_length=200,
        blank=True,
        help_text='Optional customer name'
    )
    customer_email = models.EmailField(
        verbose_name='Customer Email',
        blank=True,
        help_text='Optional customer email'
    )
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
    
    def get_display_name(self):
        """Return display name for the cart."""
        if self.customer_name:
            return f"Cart for {self.customer_name}"
        return f"Cart #{self.id}"
    
    def validate(self):
        """
        Validate the cart.
        Returns True if valid, False otherwise.
        """
        self._clear_validation_errors()
        
        # Cart validation - can be empty but has items should be valid
        return not self.has_validation_errors()
    
    # Encapsulated methods for cart calculations
    def _calculate_subtotal(self):
        """
        Private method to calculate subtotal.
        Demonstrates ENCAPSULATION by hiding calculation logic.
        """
        subtotal = Decimal('0.00')
        for item in self.cart_items.all():
            subtotal += item.get_subtotal()
        return subtotal
    
    def _calculate_tax(self):
        """Private method to calculate tax."""
        subtotal = self._calculate_subtotal()
        tax_rate = Decimal('0.10')  # 10% tax
        return subtotal * tax_rate
    
    def _calculate_total(self):
        """Private method to calculate total."""
        return self._calculate_subtotal() + self._calculate_tax()
    
    # Public methods using encapsulated logic
    def get_subtotal(self):
        """Get the subtotal for the cart."""
        return self._calculate_subtotal()
    
    def get_tax(self):
        """Get the tax amount for the cart."""
        return self._calculate_tax()
    
    def get_total(self):
        """Get the total amount for the cart."""
        return self._calculate_total()
    
    def get_item_count(self):
        """Get the total number of items in the cart."""
        return sum(item.quantity for item in self.cart_items.all())
    
    def is_empty(self):
        """Check if the cart is empty."""
        return self.get_item_count() == 0
    
    def clear_cart(self):
        """Remove all items from the cart."""
        self.cart_items.all().delete()
    
    def __str__(self):
        return f"Cart #{self.id}"


class CartItem(models.Model):
    """
    Cart item model - represents a single item in a cart.
    
    Attributes:
        cart: The cart this item belongs to
        food_item: The food item being ordered
        quantity: Quantity of the item
        notes: Optional notes for the item
    """
    
    cart = models.ForeignKey(
        Cart,
        verbose_name='Cart',
        on_delete=models.CASCADE,
        related_name='cart_items',
        help_text='The cart this item belongs to'
    )
    food_item = models.ForeignKey(
        FoodItem,
        verbose_name='Food Item',
        on_delete=models.CASCADE,
        related_name='cart_items',
        help_text='The food item being ordered'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Quantity',
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Quantity of the item'
    )
    notes = models.TextField(
        verbose_name='Notes',
        blank=True,
        help_text='Optional notes for the item'
    )
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'food_item']
    
    def get_display_name(self):
        """Return display name for the cart item."""
        return f"{self.food_item.name} x {self.quantity}"
    
    def validate(self):
        """
        Validate the cart item.
        Returns True if valid, False otherwise.
        """
        self._clear_validation_errors()
        
        if self.quantity < 1:
            self._set_validation_error("Quantity must be at least 1")
        
        if not self.food_item.is_available:
            self._set_validation_error(f"{self.food_item.name} is not available")
        
        return not self.has_validation_errors()
    
    def get_subtotal(self):
        """Get the subtotal for this cart item."""
        return self.food_item.calculate_price(self.quantity)
    
    def get_unit_price(self):
        """Get the unit price for this cart item."""
        return self.food_item.price
    
    def __str__(self):
        return f"{self.food_item.name} x {self.quantity}"
