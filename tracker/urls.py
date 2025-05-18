from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .features.budget.views import BudgetViewSet
from .features.receipt.views import ReceiptViewSet
from .features.category.views import GroceryCategoryViewSet
from .features.shopping_list.views import ShoppingListViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'receipts', ReceiptViewSet, basename='receipt')
router.register(r'categories', GroceryCategoryViewSet, basename='category')
router.register(r'shopping-lists', ShoppingListViewSet, basename='shopping-list')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
