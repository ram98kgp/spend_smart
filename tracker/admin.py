from django.contrib import admin
from .features.category.models import GroceryCategory
from .features.receipt.models import Receipt, GroceryItem
from .features.budget.models import Budget

@admin.register(GroceryCategory)
class GroceryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'unit', 'platform', 'user')
    list_filter = ('category', 'platform', 'user')
    search_fields = ('name', 'platform')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('platform', 'status', 'total_amount', 'user', 'created_at')
    list_filter = ('status', 'platform', 'user')
    search_fields = ('platform', 'user__username')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'formatted_amount', 'period', 'currency', 'formatted_threshold')
    list_filter = ('period', 'currency', 'user')
    search_fields = ('user__username',)

    def formatted_amount(self, obj):
        return f"{obj.currency_symbol}{obj.amount}"
    formatted_amount.short_description = 'Amount'

    def formatted_threshold(self, obj):
        return f"{obj.currency_symbol}{obj.notification_threshold}"
    formatted_threshold.short_description = 'Notification Threshold'
