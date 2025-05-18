from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ShoppingList, ShoppingListItem
from .serializers import ShoppingListSerializer, ShoppingListItemSerializer
from .services import SmartShoppingListGenerator

class ShoppingListViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing shopping lists and generating smart suggestions.
    """
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns shopping lists for the current user."""
        return ShoppingList.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Generate a smart shopping list based on purchase history",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Optional name for the shopping list'),
            }
        ),
        responses={
            200: ShoppingListSerializer(),
            400: 'Bad Request',
        }
    )
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a smart shopping list based on user's purchase history."""
        try:
            # Validate request data
            if not isinstance(request.data, dict):
                return Response(
                    {'error': 'Invalid request format. Expected JSON object.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get optional name parameter
            name = request.data.get('name', '')
            if name and not isinstance(name, str):
                return Response(
                    {'error': 'Invalid name parameter. Expected string.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate shopping list
            generator = SmartShoppingListGenerator(request.user)
            shopping_list = generator.generate_list(name=name)
            serializer = self.get_serializer(shopping_list)
            return Response(serializer.data)

        except Exception as e:
            import traceback
            print(f"Error generating shopping list: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to generate shopping list: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Mark items as purchased in a shopping list",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of item IDs to mark as purchased'
                ),
            },
            required=['items']
        ),
        responses={
            200: ShoppingListSerializer(),
            400: 'Bad Request',
            404: 'Not Found',
        }
    )
    @action(detail=True, methods=['post'])
    def mark_purchased(self, request, pk=None):
        """Mark specific items as purchased in the shopping list."""
        shopping_list = self.get_object()
        item_ids = request.data.get('items', [])

        if not item_ids:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update items
        items_updated = shopping_list.items.filter(id__in=item_ids).update(
            is_purchased=True,
            purchase_frequency=models.F('purchase_frequency') + 1,
            last_purchase_date=timezone.now()
        )

        # If all items are purchased, mark the list as completed
        if not shopping_list.items.filter(is_purchased=False).exists():
            shopping_list.status = 'completed'
            shopping_list.save()

        serializer = self.get_serializer(shopping_list)
        return Response(serializer.data)
