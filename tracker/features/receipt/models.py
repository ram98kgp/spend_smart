from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal

from ..category.models import GroceryCategory

def receipt_image_path(instance, filename):
    # Generate path like: receipts/user_1/2024/03/receipt_123.jpg
    ext = filename.split('.')[-1]
    new_filename = f'receipt_{timezone.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    return f'receipts/user_{instance.user.id}/{timezone.now().strftime("%Y/%m")}/{new_filename}'

class Receipt(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipts')
    image = models.ImageField(
        upload_to=receipt_image_path,
        help_text='Upload receipt image (JPEG, PNG)',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ]
    )
    platform = models.CharField(
        max_length=100,
        help_text='Name of the platform (e.g., Zepto, Blinkit)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_text = models.TextField(blank=True)
    processed_data = models.JSONField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receipt {self.id} - {self.platform} ({self.status})"

    class Meta:
        ordering = ['-created_at']

class GroceryItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(GroceryCategory, on_delete=models.SET_NULL, null=True, related_name='items')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.CharField(max_length=50, default='piece')  # e.g., kg, piece, packet
    platform = models.CharField(max_length=100)  # e.g., Zepto, Blinkit, Swiggy
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grocery_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def total_price(self):
        return self.price * self.quantity 