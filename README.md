# Indian Traffic Law AI Assistant - FastAPI Backend

## Project Overview

A FastAPI backend for an AI assistant specializing in Indian traffic laws and regulations. This system uses Google Gemini API to provide accurate, context-aware responses about traffic rules, fines, licensing procedures, and safety guidelines specific to India.

## Features

- **AI-Powered Responses**: Uses Google Gemini API with specialized prompts for Indian traffic law context
- **Conversation Management**: Create, retrieve, and manage conversation threads
- **Message History**: Maintains full conversation context for better AI responses
- **Modular Architecture**: Easy to extend and modify with clean separation of concerns
- **Database Integration**: MongoDB Atlas for scalable data storage
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Technology Stack

- **FastAPI**: Modern Python web framework for building APIs
- **MongoDB Atlas**: Cloud-based NoSQL database
- **Motor**: Asynchronous MongoDB driver for Python
- **Pydantic**: Data validation and serialization
- **Google Gemini API**: Large Language Model for AI responses
- **Uvicorn**: ASGI server for running the application

## Project Structure

```
indian_traffic_ai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── models/                # Pydantic data models
│   │   ├── __init__.py
│   │   ├── conversation.py    # Conversation data models
│   │   └── message.py         # Message data models
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py      # AI service abstraction
│   │   ├── database.py        # Database connection management
│   │   ├── conversation_service.py  # Conversation operations
│   │   └── message_service.py # Message operations
│   └── routes/                # API endpoints
│       ├── __init__.py
│       ├── conversations.py   # Conversation endpoints
│       └── chat.py           # Chat/AI interaction endpoints
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your actual environment variables
├── test_api.py              # API testing script
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (free tier available)
- Google Gemini API key

### Installation

1. **Clone the repository** (or create the project structure):

   ```bash
   mkdir indian_traffic_ai
   cd indian_traffic_ai
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   - Copy `.env.example` to `.env`
   - Fill in your actual values:

   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
   DATABASE_NAME=indian_traffic_ai
   GEMINI_API_KEY=your_gemini_api_key_here
   DEBUG=true
   ```

5. **Get required API keys**:
   - **MongoDB Atlas**:
     - Sign up at [mongodb.com/atlas](https://mongodb.com/atlas)
     - Create a free cluster
     - Get connection string from "Connect" → "Connect your application"
   - **Gemini API**:
     - Visit [Google AI Studio](https://makersuite.google.com)
     - Create an API key

### Running the Application

1. **Start the server**:

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/ask` - Ask a question about Indian traffic laws

### Conversation Management

- `POST /api/v1/conversations/` - Create a new conversation
- `GET /api/v1/conversations/` - Get all conversations
- `GET /api/v1/conversations/{id}` - Get specific conversation
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### System Endpoints

- `GET /` - Root endpoint (API information)
- `GET /health` - Health check endpoint

## Usage Examples

### Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the penalty for not wearing a helmet?"}'
```

### Continue a Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about for two-wheeler riders?",
    "conversation_id": "60f8b2c8e8b4a1234567890a"
  }'
```

### Create a Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Traffic Fine Questions"}'
```

## Architecture Highlights

### Modular Design

- **Services Layer**: Business logic separated from API routes
- **Models Layer**: Data validation and serialization using Pydantic
- **Routes Layer**: HTTP request handling and response formatting
- **Database Layer**: Async MongoDB operations with Motor

### AI Service Abstraction

The AI service is designed to be easily replaceable:

```python
# Current implementation
def get_ai_service() -> AIServiceInterface:
    return GeminiAIService()

# Easy to swap to different providers
def get_ai_service() -> AIServiceInterface:
    return OpenAIService()  # or CustomLLMService(), etc.
```

### Error Handling

- Comprehensive error handling at all layers
- Meaningful HTTP status codes and error messages
- Proper logging for debugging and monitoring

## Database Schema

### Conversations Collection

```json
{
  "_id": "ObjectId",
  "title": "string",
  "user_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "integer"
}
```

### Messages Collection

```json
{
  "_id": "ObjectId",
  "conversation_id": "string",
  "role": "user|assistant",
  "content": "string",
  "timestamp": "datetime"
}
```

## Testing

### Manual Testing

Run the included test script:

```bash
python test_api.py
```

### Interactive Testing

Use the automatic API documentation:

```
http://localhost:8000/docs
```

## Deployment

### Environment Variables for Production

```env
MONGODB_URL=your_production_mongodb_url
DATABASE_NAME=indian_traffic_ai_prod
GEMINI_API_KEY=your_production_gemini_key
DEBUG=false
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

This application is ready to deploy on:

- **Railway**: Connect GitHub repo, set environment variables
- **Render**: Deploy from GitHub, configure environment
- **Heroku**: Use Procfile: `web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}`

## Future Enhancements

### User Authentication

- JWT-based authentication system
- User registration and login
- Protected routes and user-specific data

### Additional Features

- Message editing and deletion
- Conversation search functionality
- Export conversation history
- Rate limiting and API quotas
- Caching layer for improved performance

### AI Improvements

- Support for multiple AI providers
- Custom training on Indian traffic law datasets
- Image recognition for traffic signs
- Voice input/output capabilities

## Troubleshooting

### Common Issues

1. **Database Connection Error**:

   - Verify MongoDB Atlas connection string
   - Check IP whitelist in Atlas dashboard
   - Ensure network connectivity

2. **Gemini API Error**:

   - Verify API key is correct
   - Check API quota and usage limits
   - Ensure API key has proper permissions

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check Python path configuration

## Contributing

This is a B.Tech final year project focused on learning FastAPI, MongoDB, and AI integration. The code prioritizes clarity and educational value over performance optimization.

## License

Educational project - please adapt and modify as needed for your learning journey.

## Contact

For questions about this implementation, please refer to the code comments and documentation.
