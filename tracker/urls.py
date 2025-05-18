from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .features.category.views import GroceryCategoryViewSet
from .features.receipt.views import ReceiptViewSet, GroceryItemViewSet
from .features.budget.views import BudgetViewSet
from .features.shopping_list.views import ShoppingListViewSet

router = DefaultRouter()
router.register(r'categories', GroceryCategoryViewSet, basename='category')
router.register(r'receipts', ReceiptViewSet, basename='receipt')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'shopping-lists', ShoppingListViewSet, basename='shopping-list')

urlpatterns = [
    path('', include(router.urls)),
] 