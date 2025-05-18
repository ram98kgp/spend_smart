from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema

from .models import Budget
from .serializers import BudgetSerializer, BudgetAnalyticsSerializer
from ..utils import send_budget_notification
from ..receipt.models import GroceryItem

class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing budgets and viewing analytics.
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns budgets for the current user.
        """
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get budget analytics for the current period",
        responses={
            200: BudgetAnalyticsSerializer(many=True)
        }
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get budget analytics for the current period."""
        today = timezone.now().date()
        
        # Get the active budget for the user
        try:
            budget = self.get_queryset().latest('created_at')
        except Budget.DoesNotExist:
            return Response({
                'error': 'No budget found. Please set a budget first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate the start date based on the budget period
        if budget.period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
        else:  # monthly
            start_date = today.replace(day=1)

        # Calculate total spent amount for the period
        spent = GroceryItem.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=today
        ).aggregate(total=Sum('price'))['total'] or Decimal('0')

        # Check if we need to send a notification
        if budget.should_send_notification(spent):
            try:
                send_budget_notification(request.user, budget, spent)
                budget.notification_sent = True
                budget.save()
            except Exception as e:
                print(f"Failed to send budget notification: {e}")

        # Get spending by category for the period
        category_spending = GroceryItem.objects.filter(
            user=request.user,
            created_at__date__gte=start_date,
            created_at__date__lte=today
        ).values('category__name').annotate(
            total=Sum('price')
        ).order_by('-total')

        remaining = budget.amount - spent

        response_data = {
            'period': budget.period,
            'budget_amount': budget.amount,
            'spent_amount': spent,
            'remaining_amount': remaining,
            'notification_threshold': budget.notification_threshold,
            'notification_sent': budget.notification_sent,
            'category_breakdown': [
                {
                    'category_name': item['category__name'],
                    'spent_amount': item['total'],
                    'percentage_of_total': (item['total'] / spent * 100) if spent > 0 else Decimal('0')
                } for item in category_spending
            ]
        }

        return Response(response_data) 