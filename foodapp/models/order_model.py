"""
Order Models Module

This module defines order-related models demonstrating:
- INHERITANCE: OnlineOrder inherits from Order
- POLYMORPHISM: calculate_total() behaves differently based on order type
- ENCAPSULATION: Private methods for order calculations
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .base_models import BaseModel
from .food_model import FoodItem


class Order(BaseModel):
    
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PREPARING = 'PREPARING', 'Preparing'
        READY = 'READY', 'Ready'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    # Order type choices
    class OrderType(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        ONLINE = 'ONLINE', 'Online'
    
    order_number = models.CharField(
        verbose_name='Order Number',
        max_length=20,
        unique=True,
        help_text='Unique order identifier'
    )
    customer_name = models.CharField(
        verbose_name='Customer Name',
        max_length=200,
        help_text='Name of the customer'
    )
    customer_email = models.EmailField(
        verbose_name='Customer Email',
        help_text='Email of the customer'
    )
    customer_phone = models.CharField(
        verbose_name='Customer Phone',
        max_length=20,
        help_text='Phone number of the customer'
    )
    status = models.CharField(
        verbose_name='Status',
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text='Current status of the order'
    )
    order_type = models.CharField(
        verbose_name='Order Type',
        max_length=10,
        choices=OrderType.choices,
        default=OrderType.BASIC,
        help_text='Type of order'
    )
    total_amount = models.DecimalField(
        verbose_name='Total Amount',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Total amount for the order'
    )
    delivery_address = models.TextField(
        verbose_name='Delivery Address',
        blank=True,
        help_text='Delivery address'
    )
    special_instructions = models.TextField(
        verbose_name='Special Instructions',
        blank=True,
        help_text='Special instructions for the order'
    )
    
    # Online order specific fields
    payment_method = models.CharField(
        verbose_name='Payment Method',
        max_length=20,
        blank=True,
        choices=[
            ('CREDIT_CARD', 'Credit Card'),
            ('DEBIT_CARD', 'Debit Card'),
            ('PAYPAL', 'PayPal'),
            ('CASH', 'Cash on Delivery'),
        ],
        help_text='Method of payment'
    )
    payment_status = models.CharField(
        verbose_name='Payment Status',
        max_length=20,
        blank=True,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded'),
        ],
        help_text='Status of the payment'
    )
    delivery_notes = models.TextField(
        verbose_name='Delivery Notes',
        blank=True,
        help_text='Additional delivery notes'
    )
    estimated_delivery_time = models.PositiveIntegerField(
        verbose_name='Estimated Delivery Time (minutes)',
        default=45,
        blank=True,
        validators=[MinValueValidator(15)],
        help_text='Estimated delivery time'
    )
    
    # Private attribute for discount calculation
    _discount_percentage = Decimal('0.00')
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def get_display_name(self):
        """Return display name for the order."""
        return f"Order #{self.order_number}"
    
    def validate(self):
        """
        Validate the order.
        Returns True if valid, False otherwise.
        """
        self._clear_validation_errors()
        
        if not self.customer_name:
            self._set_validation_error("Customer name is required")
        
        if not self.customer_email:
            self._set_validation_error("Customer email is required")
        
        if not self.order_number:
            self._set_validation_error("Order number is required")
        
        return not self.has_validation_errors()
    
    def calculate_total(self):
        total = Decimal('0.00')
        
        for item in self.order_items.all():
            item_total = item.food_item.price * item.quantity
            total += item_total
        

        if self._discount_percentage > 0:
            total = self._apply_discount(total, self._discount_percentage)
        
        if self.order_type == self.OrderType.ONLINE:
            delivery_fee = Decimal('5.00')
            total += delivery_fee
        
        return total
    
    def _apply_discount(self, amount, discount_percentage):
        """
         ENCAPSULATION by hiding discount calculation logic.
        """
        if discount_percentage > 0:
            discount = amount * (discount_percentage / 100)
            return amount - discount
        return amount
    
    def can_cancel(self):
        if self.status not in [self.OrderStatus.PENDING, self.OrderStatus.CONFIRMED]:
            return False
        
        # Can't cancel online orders if payment is completed
        if self.order_type == self.OrderType.ONLINE and self.payment_status == 'COMPLETED':
            return False
        
        return True
    
    def update_status(self, new_status):
        """Update the order status."""
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
    
    def get_total_items(self):
        """Get the total number of items in the order."""
        return sum(item.quantity for item in self.order_items.all())
    
    def __str__(self):
        return f"Order #{self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Order',
        on_delete=models.CASCADE,
        related_name='order_items',
        help_text='The order this item belongs to'
    )
    food_item = models.ForeignKey(
        FoodItem,
        verbose_name='Food Item',
        on_delete=models.PROTECT,
        related_name='order_items',
        help_text='The food item'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Quantity',
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Quantity of the food item'
    )
    unit_price = models.DecimalField(
        verbose_name='Unit Price',
        max_digits=10,
        decimal_places=2,
        help_text='Price at the time of order'
    )
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def get_display_name(self):
        return f"{self.food_item.name} x {self.quantity}"
    
    def calculate_subtotal(self):
        return self.unit_price * self.quantity
    
    def __str__(self):
        return f"{self.food_item.name} x {self.quantity}"
