# Indian Traffic Law AI Assistant - FastAPI Backend

## Project Overview

A FastAPI backend for an AI assistant specializing in Indian traffic laws and regulations. This system uses Google Gemini API to provide accurate, context-aware responses about traffic rules, fines, licensing procedures, and safety guidelines specific to India.

## Features

- **AI-Powered Responses**: Uses Google Gemini API with specialized prompts for Indian traffic law context
- **User Authentication**: JWT-based authentication with registration and login
- **Secure Conversations**: User-specific conversation management with access control
- **Message History**: Maintains full conversation context for better AI responses
- **Modular Architecture**: Easy to extend and modify with clean separation of concerns
- **Database Integration**: MongoDB Atlas for scalable data storage
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Access Control**: Users can only access their own conversations and data

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
│   │   ├── message.py         # Message data models
│   │   └── user.py           # User and authentication models
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py      # AI service abstraction
│   │   ├── auth_service.py    # Authentication and JWT handling
│   │   ├── database.py        # Database connection management
│   │   ├── conversation_service.py  # Conversation operations
│   │   ├── message_service.py # Message operations
│   │   ├── user_service.py    # User operations
│   │   └── dependencies.py    # FastAPI authentication dependencies
│   └── routes/                # API endpoints
│       ├── __init__.py
│       ├── auth.py           # Authentication endpoints
│       ├── conversations.py   # Conversation endpoints
│       └── chat.py           # Chat/AI interaction endpoints
├── tests/                     # Test files
│   ├── test_api.py           # Basic API testing
│   ├── test_auth_endpoints.py # Authentication testing
│   ├── test_authenticated_api.py # Complete system testing
│   └── debug_registration.py  # Debug utilities
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your actual environment variables
├── Dockerfile                # Container deployment
├── .dockerignore            # Docker optimization
├── Procfile                 # Heroku deployment
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

   **Dependencies include**:

   - `fastapi` - Web framework
   - `uvicorn` - ASGI server
   - `motor` - Async MongoDB driver
   - `pydantic` - Data validation
   - `google-generativeai` - Gemini API client
   - `python-jose[cryptography]` - JWT token handling
   - `passlib[bcrypt]` - Password hashing
   - `python-multipart` - Form data support

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

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register a new user account
- `POST /api/v1/auth/login` - Login with email and password
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/logout` - Logout current user

### Chat Endpoints (🔒 Requires Authentication)

- `POST /api/v1/chat/ask` - Ask a question about Indian traffic laws

### Conversation Management (🔒 Requires Authentication)

- `POST /api/v1/conversations/` - Create a new conversation
- `GET /api/v1/conversations/` - Get all user's conversations
- `GET /api/v1/conversations/{id}` - Get specific conversation
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### System Endpoints

- `GET /` - Root endpoint (API information)
- `GET /health` - Health check endpoint

## Usage Examples

### Authentication Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword123"
  }'

# Response includes access_token
# {"access_token": "eyJ...", "token_type": "bearer", "user": {...}}

# 2. Or login with existing account
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Ask a Question (Authenticated)

```bash
# Use the token from registration/login
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "What is the penalty for not wearing a helmet?"}'
```

### Continue a Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What about for two-wheeler riders?",
    "conversation_id": "60f8b2c8e8b4a1234567890a"
  }'
```

### Create a Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Traffic Fine Questions"}'
```

### Get User's Conversations

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
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

### Users Collection

```json
{
  "_id": "ObjectId",
  "email": "string (unique)",
  "full_name": "string",
  "hashed_password": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Conversations Collection

```json
{
  "_id": "ObjectId",
  "title": "string",
  "user_id": "string (references Users._id)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "integer"
}
```

### Messages Collection

```json
{
  "_id": "ObjectId",
  "conversation_id": "string (references Conversations._id)",
  "role": "user|assistant",
  "content": "string",
  "timestamp": "datetime"
}
```

## Testing

### Automated Testing

Run the comprehensive test suite:

```bash
# Test basic authentication
python tests/test_auth_endpoints.py

# Test complete authenticated system
python tests/test_authenticated_api.py

# Test basic API functionality
python tests/test_api.py
```

### Manual Testing Workflow

1. **Start the server**:

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Register a new user** (via API docs at http://localhost:8000/docs):

   - Go to `/api/v1/auth/register`
   - Provide email, full_name, and password
   - Copy the `access_token` from response

3. **Authorize in API docs**:

   - Click "Authorize" button at top of docs page
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

4. **Test chat functionality**:

   - Use `/api/v1/chat/ask` endpoint
   - Ask questions like "What is the speed limit in India?"
   - Try follow-up questions with the same `conversation_id`

5. **Test conversation management**:
   - View your conversations with `/api/v1/conversations/`
   - Get specific conversation details
   - View messages in conversations

### Interactive Testing

Use the automatic API documentation at:

```
http://localhost:8000/docs
```

### Test Data Examples

Use these sample questions for testing:

- "What documents do I need for a driving license in India?"
- "What is the penalty for overspeeding?"
- "How much is the fine for not wearing a helmet?"
- "What are the rules for parking in residential areas?"
- "Do I need insurance for a motorcycle?"

## Security Features

### Password Security

- Bcrypt hashing for all passwords
- Minimum password length requirements
- No plain text password storage

### JWT Token Security

- Stateless authentication using JWT tokens
- 30-minute token expiration
- Bearer token authentication scheme
- Secure token verification

### Access Control

- User-specific data isolation
- Conversation ownership validation
- Protected routes requiring authentication
- Proper HTTP status codes for unauthorized access

### Data Validation

- Pydantic models for all API inputs
- Email format validation
- Comprehensive error handling
- Input sanitization

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

### Advanced Authentication

- Password reset functionality
- Email verification for new accounts
- OAuth integration (Google, Facebook login)
- Role-based access control (admin, user roles)

### Additional Features

- Message editing and deletion
- Conversation search functionality
- Export conversation history
- Rate limiting and API quotas
- Caching layer for improved performance
- Real-time chat with WebSocket support

### AI Improvements

- Support for multiple AI providers
- Custom training on Indian traffic law datasets
- Image recognition for traffic signs
- Voice input/output capabilities
- Multi-language support (Hindi, regional languages)

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

3. **Authentication Issues**:

   - **401 Unauthorized**: Check JWT token format and validity
   - **403 Forbidden**: User trying to access resources they don't own
   - **Token expired**: Tokens expire in 30 minutes, need to login again
   - **Invalid credentials**: Check email/password combination

4. **Import Errors**:

   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check Python path configuration

5. **Validation Errors**:
   - Check email format (must be valid email)
   - Ensure password meets minimum length (6 characters)
   - Verify all required fields are provided

### Debug Tips

1. **Check server logs**: Most errors are logged with detailed information
2. **Use API docs**: Test endpoints interactively at `/docs`
3. **Verify environment variables**: Ensure `.env` file has all required values
4. **Test authentication flow**: Register → Login → Use token for protected endpoints

## Contributing

This is a B.Tech final year project focused on learning FastAPI, MongoDB, and AI integration. The code prioritizes clarity and educational value over performance optimization.

## License

Educational project - please adapt and modify as needed for your learning journey.

## Contact

For questions about this implementation, please refer to the code comments and documentation.
