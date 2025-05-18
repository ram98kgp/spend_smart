from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import GroceryCategory
from .serializers import GroceryCategorySerializer

class GroceryCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing grocery categories.
    """
    queryset = GroceryCategory.objects.all()
    serializer_class = GroceryCategorySerializer
    permission_classes = [IsAuthenticated] 