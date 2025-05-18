from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Budget(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('INR', 'Indian Rupee (₹)'),
        ('JPY', 'Japanese Yen (¥)'),
    ]

    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Currency for the budget amount"
    )
    notification_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount at which to send notification (e.g., 800 for $800)"
    )
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'period']

    def __str__(self):
        currency_symbol = self.CURRENCY_SYMBOLS.get(self.currency, self.currency)
        return f"Grocery Budget - {currency_symbol}{self.amount} ({self.period})"

    def should_send_notification(self, current_spent):
        """
        Check if notification should be sent based on current spent amount
        """
        return (not self.notification_sent and 
                current_spent >= self.notification_threshold)

    @property
    def currency_symbol(self):
        """
        Get the currency symbol for this budget
        """
        return self.CURRENCY_SYMBOLS.get(self.currency, self.currency) 