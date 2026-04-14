from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True
    
    _validation_errors = []
    
   
    created_at = models.DateTimeField(
        verbose_name='Created At',
        auto_now_add=True,
        help_text='Timestamp when the record was created'
    )
    updated_at = models.DateTimeField(
        verbose_name='Updated At',
        auto_now=True,
        help_text='Timestamp when the record was last updated'
    )
    is_active = models.BooleanField(
        verbose_name='Is Active',
        default=True,
        help_text='Soft delete flag - inactive records are not deleted'
    )

    def get_display_name(self):
        raise NotImplementedError("Subclasses must implement get_display_name()")
    
    def validate(self):
        raise NotImplementedError("Subclasses must implement validate()")
    
    def _set_validation_error(self, error_message):
        self._validation_errors.append(error_message)
    
    def _get_validation_errors(self):
        return self._validation_errors.copy()
    
    def _clear_validation_errors(self):
        self._validation_errors = []
    
    def has_validation_errors(self):
        return len(self._validation_errors) > 0
    
    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def restore(self):
        """Restore a soft-deleted model instance."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
    
    def get_time_since_creation(self):
        delta = timezone.now() - self.created_at
        return delta
    
    def __str__(self):
        return self.get_display_name()


class BaseOrder(BaseModel):  
    class Meta:
        abstract = True
    
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PREPARING = 'PREPARING', 'Preparing'
        READY = 'READY', 'Ready'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    @property
    def order_type(self):
        raise NotImplementedError("Subclasses must implement order_type property")
    
    def calculate_total(self):
        raise NotImplementedError("Subclasses must implement calculate_total()")
    
    def can_cancel(self):
        raise NotImplementedError("Subclasses must implement can_cancel()")
    
    def _validate_order_items(self):
        return True
    
    def _apply_discount(self, amount, discount_percentage):

        if discount_percentage > 0:
            discount = amount * (discount_percentage / 100)
            return amount - discount
        return amount
    
    def get_status_display_class(self):
        """Get CSS class for status display."""
        status_classes = {
            'PENDING': 'warning',
            'CONFIRMED': 'info',
            'PREPARING': 'primary',
            'READY': 'success',
            'DELIVERED': 'success',
            'CANCELLED': 'danger',
        }
        return status_classes.get(self.status, 'secondary')
