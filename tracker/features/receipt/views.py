from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import openai
import base64
import json
from django.conf import settings

from .models import Receipt, GroceryItem
from .serializers import ReceiptSerializer, GroceryItemSerializer
from ..category.models import GroceryCategory

class ReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing receipts and processing receipt images.
    """
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Upload and process a receipt image",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Receipt image file (JPEG, PNG format)'
            ),
            openapi.Parameter(
                'platform',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description='Platform name (e.g., Zepto, Blinkit)'
            ),
        ],
        responses={
            201: ReceiptSerializer(),
            400: 'Bad Request',
            415: 'Unsupported Media Type'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns receipts for the current user.
        """
        return Receipt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        receipt = serializer.save(user=self.request.user)
        self.process_receipt(receipt.id)

    @staticmethod
    def process_receipt(receipt_id):
        receipt = Receipt.objects.get(id=receipt_id)
        receipt.status = 'processing'
        receipt.save()

        try:
            # Read the image file and encode it as base64
            with open(receipt.image.path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Get all available categories
            categories = GroceryCategory.objects.all()
            category_names = [cat.name for cat in categories]
            category_dict = {cat.name: cat for cat in categories}

            # Use OpenAI Vision API to analyze the receipt
            prompt = f"""
            You are a receipt analyzer. Look at this receipt image and extract the following information:
            1. Store/Platform name (if visible)
            2. Total amount
            3. List of items with:
               - Item name
               - Quantity
               - Unit price
               - Total price
            
            Also categorize each item into one of these categories: {', '.join(category_names)}
            
            Return the data in this exact JSON format:
            {{
                "platform": "store name",
                "total_amount": "numeric total",
                "items": [
                    {{
                        "name": "item name",
                        "quantity": "numeric quantity",
                        "unit_price": "numeric price",
                        "total_price": "numeric total",
                        "category": "one of the provided category names"
                    }}
                ]
            }}

            Make sure to:
            1. Return ONLY the JSON, no other text
            2. Use numeric values without currency symbols
            3. Assign each item to the most appropriate category
            4. If unsure about category, use "Others"
            """

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )

            structured_data = response.choices[0].message.content
            print(f"Structured data: {structured_data}")
            # Clean the response from markdown formatting
            if structured_data.startswith('```'):
                # Remove the first line (```json) and the last line (```)
                structured_data = '\n'.join(structured_data.split('\n')[1:-1])
            
            receipt.processed_data = structured_data
            receipt.status = 'completed'

            # Create GroceryItems from the processed data
            try:
                data = json.loads(structured_data)
                receipt.total_amount = float(data['total_amount'])
                receipt.save()

                # Create grocery items with categories
                for item in data['items']:
                    category = category_dict.get(item['category'], category_dict['Others'])
                    GroceryItem.objects.create(
                        user=receipt.user,
                        name=item['name'],
                        quantity=float(item['quantity']),
                        price=float(item['unit_price']),
                        platform=data['platform'],
                        category=category
                    )
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Received data: {structured_data}")
                receipt.status = 'failed'
                receipt.processed_data = {'error': f'Invalid JSON format: {str(e)}'}
                receipt.save()
            except Exception as e:
                receipt.status = 'failed'
                receipt.processed_data = {'error': str(e)}
                print(f"Error in processing receipt: {e}")
                receipt.save()

        except Exception as e:
            receipt.status = 'failed'
            receipt.processed_data = {'error': str(e)}
            print(f"Error in processing receipt: {e}")
            receipt.save()

class GroceryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing grocery items.
    """
    serializer_class = GroceryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns grocery items for the current user.
        """
        return GroceryItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 