# SpendSmart - Grocery Expense Tracker

SpendSmart is a Django-based application that helps users track and analyze their grocery expenses by automatically processing receipt images and categorizing items using AI.

## Key Features

- **Receipt Processing**:
  - Upload and process grocery receipts from various platforms
  - Automatic text extraction using OpenAI Vision API
  - Smart item categorization based on AI analysis
  - Support for image uploads in base64 format

- **Budget Management**:
  - Set and monitor overall grocery budgets
  - Track spending across different categories
  - Get notifications when approaching budget limits
  - View detailed spending analytics

- **Category Management**:
  - Pre-configured grocery categories
  - Custom category creation
  - Category-wise expense tracking
  - Smart category suggestions for new items

- **Item Management**:
  - Automatic item detection from receipts
  - Price tracking over time
  - Item categorization
  - Purchase history

## Technical Requirements

- Python 3.9+
- Redis (for Celery)
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd spend_smart
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file in the project root and add:
   ```
   DEBUG=True
   DJANGO_SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   REDIS_URL=redis://localhost:6379/0
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py load_categories
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. Start Redis server (required for Celery):
   ```bash
   redis-server
   ```

2. Start Celery worker (in a new terminal):
   ```bash
   celery -A spend_smart worker --loglevel=info
   ```

3. Start Celery beat for scheduled tasks (in another terminal):
   ```bash
   celery -A spend_smart beat --loglevel=info
   ```

4. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

5. Access the application:
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - API documentation: http://localhost:8000/swagger/

## API Usage Guide

### Receipt Processing API

**Endpoint**: `POST /api/receipts/`

**Request Format**:
```json
{
    "image": "base64_encoded_image_string",
    "platform": "Platform Name"
}
```

**Response Format**:
```json
{
    "id": 1,
    "items": [
        {
            "name": "Product Name",
            "quantity": 1,
            "price": 10.99,
            "category": "Category Name",
            "unit": "piece"
        }
    ],
    "total_amount": 10.99,
    "platform": "Platform Name",
    "status": "processing",
    "created_at": "YYYY-MM-DD HH:MM:SS"
}
```

### Budget Management API

**Create Budget**:
```json
POST /api/budgets/
{
    "amount": 500.00,
    "period": "monthly",
    "currency": "USD",
    "notification_threshold": 400.00
}
```

**Response Format**:
```json
{
    "id": 1,
    "amount": 500.00,
    "period": "monthly",
    "currency": "USD",
    "notification_threshold": 400.00,
    "notification_sent": false,
    "currency_symbol": "$"
}
```

### Categories API

**List Categories**:
```bash
GET /api/categories/
```

**Create Category**:
```json
POST /api/categories/
{
    "name": "Category Name",
    "description": "Category Description"
}
```

## OpenAI Vision API Integration

The application uses OpenAI's Vision API for receipt processing. The API analyzes receipt images and returns structured data including:
- Item names
- Prices
- Quantities
- Platform information (e.g., Zepto, Blinkit)
- Units (e.g., piece, kg, packet)

The system processes this information through the following steps:
1. Image is converted to base64
2. OpenAI Vision API analyzes the image
3. Response is parsed and cleaned
4. Items are automatically categorized and stored with their respective units and platform information

## Celery Tasks

The application uses Celery for background task processing:


1. **Budget Monitoring**:
   - Task: `check_budget_thresholds`
   - Runs periodically (daily)
   - Sends notifications for budget thresholds

## Error Handling

The application includes robust error handling for:
- Invalid image formats
- Budget overflow scenarios
- Database constraints

## Security Considerations

- API authentication required for all endpoints
- Secure handling of API keys
- Input validation and sanitization
- File upload restrictions

## Monitoring and Logging

- Celery task monitoring via Flower
- Application logs in `logs/` directory
- Error tracking and reporting
- Performance metrics collection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 