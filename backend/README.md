# ADOGENT Backend - AI-Powered E-Commerce Platform

Modern FastAPI backend with AI agents, async database operations, and Groq LLM integration.

## 🚀 Quick Start

```bash
# Using Docker Compose
docker-compose up --build

# Or manually
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📁 Project Structure

```
backend/
├── app/                          # Core application
│   ├── main.py                  # FastAPI application entry point
│   ├── api/                     # API route handlers (async)
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── health.py           # Health check endpoints
│   │   ├── products.py         # Product management endpoints
│   │   ├── recommendations.py  # AI recommendation endpoints
│   │   └── users.py            # User management endpoints
│   ├── agents/                  # AI agents and Groq integrations
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Base AI agent class
│   │   ├── product_agent.py    # Product recommendation agent
│   │   ├── voice_agent.py      # Voice interaction agent
│   │   └── support_agent.py    # Customer support agent
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── config.py           # Application settings
│   ├── db/                      # Database setup and connections
│   │   ├── __init__.py
│   │   └── database.py         # Async SQLAlchemy setup
│   ├── logging/                 # Centralized logging
│   │   ├── __init__.py
│   │   └── log.py              # Structured JSON logging
│   ├── models/                  # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── base_model.py       # Base model with UUID and timestamps
│   │   ├── user.py             # User model with preferences
│   │   └── user_session.py     # Session management model
│   ├── schemas/                 # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── auth_schemas.py     # Authentication schemas
│   │   └── user_schemas.py     # User management schemas
│   ├── services/                # Business logic layer (async)
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication service
│   │   ├── user_service.py     # User management service
│   │   └── ai_service.py       # AI agent orchestration
│   └── utils/                   # Shared utilities
│       ├── __init__.py
│       ├── security.py         # Password hashing, JWT tokens
│       └── exceptions.py       # Custom exception classes
├── alembic/                     # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Migration template
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── test_auth.py            # Authentication tests
│   ├── test_users.py           # User management tests
│   └── test_agents.py          # AI agent tests
├── logs/                        # Log files (auto-created)
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Development environment
├── Dockerfile                  # Container definition
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## ⚡ Technology Stack

### Core Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework with async support
- **[Python 3.11+](https://python.org)** - Latest Python with enhanced async performance
- **[Pydantic](https://pydantic.dev/)** - Data validation using Python type hints
- **[Uvicorn](https://uvicorn.org/)** - Lightning-fast ASGI server

### Database & ORM
- **[SQLAlchemy](https://sqlalchemy.org/)** - Async ORM for database operations
- **[PostgreSQL](https://postgresql.org/)** - Robust relational database
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration management
- **[asyncpg](https://github.com/MagicStack/asyncpg)** - Fast PostgreSQL adapter

### AI & ML
- **[Groq](https://groq.com/)** - Ultra-fast LLM API for AI agents
- **Custom AI Agents** - Specialized agents for e-commerce functions
- **Natural Language Processing** - Advanced text and voice processing

### Security & Authentication
- **[passlib](https://passlib.readthedocs.io/)** - Password hashing with bcrypt
- **[python-jose](https://github.com/mpdavis/python-jose)** - JWT token management
- **OAuth 2.0** - Modern authentication flows

### Development & Deployment
- **[Docker](https://docker.com/)** - Containerization for consistent deployments
- **[pytest](https://pytest.org/)** - Comprehensive testing framework
- **[Black](https://black.readthedocs.io/)** - Code formatting
- **[Ruff](https://github.com/astral-sh/ruff)** - Fast Python linter

## 🏗️ Architecture Principles

### Async-First Design
- All database operations use `async`/`await` patterns
- Non-blocking I/O for maximum performance
- Async service layer for business logic
- Concurrent AI agent processing

### Modular Structure
- **Services Layer**: Business logic separated from API routes
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Clean dependency management
- **Event-Driven**: Async event handling for complex workflows

### Security & Compliance
- JWT tokens with refresh mechanism
- Password hashing with bcrypt
- Rate limiting and request validation
- Structured logging for audit trails

## 🗄️ Database Models

### User Management
- **User**: Core user model with preferences and security fields
- **UserSession**: JWT session management with device tracking
- **Role-Based Access**: Customer, Admin, Moderator roles

### Features
- UUID primary keys for all models
- Soft delete functionality
- Automatic timestamps (created_at, updated_at)
- Async relationship loading

## 🤖 AI Agent System

### Agent Types
- **Product Agent**: Intelligent product recommendations
- **Voice Agent**: Natural language voice interactions
- **Support Agent**: Customer service automation
- **Shopping Agent**: Personalized shopping assistance

### Groq Integration
- Ultra-fast LLM API calls
- Model selection based on use case
- Token usage tracking and optimization
- Error handling and fallback strategies

## 📊 Logging & Monitoring

### Structured Logging
- JSON-formatted logs for easy parsing
- Weekly log rotation (12 weeks retention)
- Contextual logging with user/session tracking
- Separate error log files

### Monitoring Points
- API request/response times
- Database operation performance
- AI agent interaction metrics
- User behavior analytics

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/adogent
REDIS_URL=redis://localhost:6379

# AI Services
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=ADOGENT
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO
LOG_DIR=logs

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd adogent/backend

# Install dependencies
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Structure
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Agent Tests**: AI agent functionality with mocked APIs
- **Database Tests**: Async database operations

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t adogent-backend .

# Run container
docker run -p 8000:8000 adogent-backend

# Using Docker Compose
docker-compose up --build
```

### Production Considerations
- Use environment-specific configuration
- Enable proper logging and monitoring
- Configure load balancing for high availability
- Set up database connection pooling
- Implement proper error handling and retry logic

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Key Endpoints
```
POST /api/auth/register     # User registration
POST /api/auth/login        # User login
POST /api/auth/refresh      # Token refresh
GET  /api/users/profile     # User profile
POST /api/agents/chat       # AI chat interaction
GET  /api/products/search   # Product search
POST /api/orders            # Order creation
```

## 🔄 Development Workflow

### Code Quality
```bash
# Format code
black app/

# Lint code
ruff check app/

# Type checking
mypy app/

# Run tests
pytest
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## 🛠️ Troubleshooting

### Common Issues
1. **Database Connection**: Check DATABASE_URL format
2. **Migration Errors**: Ensure database is running
3. **Import Errors**: Check Python path and dependencies
4. **Async Issues**: Ensure all database operations use async/await

### Performance Optimization
- Use connection pooling for database
- Implement caching for frequent queries
- Optimize AI agent calls with batching
- Monitor and profile async operations

---

## 📝 Contributing

1. Follow the async-first architecture
2. Write comprehensive tests for new features
3. Use structured logging for debugging
4. Follow PEP 8 style guidelines
5. Document all public APIs

---

**Built with ❤️ using FastAPI and modern Python async patterns**