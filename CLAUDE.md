# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ADOGENT is an AI-powered luxury e-commerce platform with:
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Groq AI
- **Architecture**: Microservices with specialized AI agents (mixed sync/async patterns)
- **Deployment**: Backend deployed at https://adogent.onrender.com

## Essential Commands

### Frontend Development
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server (port 8080)
npm run build        # Production build
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Backend Development
```bash
cd backend
# Install dependencies (Note: requirements-dev.txt needs to be populated)
pip install fastapi uvicorn sqlalchemy asyncpg alembic groq pydantic python-jose passlib bcrypt python-dotenv psycopg2-binary
pip install -r requirements-dev.txt  # Install dev dependencies (when fixed)

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Code quality
black app/           # Format code
ruff check app/      # Lint code  
mypy app/            # Type checking

# Testing
pytest                          # Run all tests
pytest --cov=app --cov-report=html  # With coverage report
pytest tests/api/test_products.py   # Specific test file
pytest -k "test_name"               # Specific test by name
pytest -v                           # Verbose output

# Database
alembic upgrade head                    # Run migrations
alembic revision --autogenerate -m "message"  # Create migration
alembic current                         # Check migration status
```

### Docker Development
```bash
cd backend/docker
docker-compose up --build    # Start full stack
# Backend: http://localhost:8008 (mapped from container port 8000)
# PostgreSQL: http://localhost:7660
# API Docs: http://localhost:8008/docs
```

## Architecture Overview

### AI Agent System
The platform uses specialized AI agents (`backend/app/agents/`):
- **BaseAgent**: Abstract base class with conversation management
- **ProductAgent**: Product discovery and search
- **RecommendationAgent**: Personalized ML-driven suggestions
- **SupportAgent**: Customer service automation
- **VoiceAgent**: Voice interaction with NLP processing

Agents use Groq's ultra-fast LLM API with Ollama as multimodal fallback.

### Backend Architecture
- **FastAPI Smart Handling**: FastAPI intelligently handles both sync and async functions - use async for I/O operations, sync is fine for simple operations
- **Service Layer Pattern**: Business logic separated from API routes (`app/services/`)
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Clean dependency management
- **Mixed Sync/Async**: FastAPI runs sync functions in thread pools automatically, preventing blocking
- **Database**: PostgreSQL with SQLAlchemy (supports both sync and async operations)
- **Authentication**: JWT tokens with role-based access control (Admin, Moderator, User)
- **Security**: bcrypt password hashing, OAuth 2.0 flows

### Frontend Architecture
- **Pages** (`src/pages/`): Main application routes
- **Components** (`src/components/`): Reusable UI components using shadcn/ui
- **API Client**: TanStack Query for data fetching with caching
- **State Management**: React hooks and context
- **Styling**: Tailwind CSS with custom theme and animations

## Current Project Status (from TODO.md)

### Current Sprint Priorities
1. **Fix Ollama connectivity** - Service startup and model availability issues
2. **Implement ProductService** - Complete async product management
3. **Create Product API endpoints** - CRUD operations
4. **Add comprehensive test coverage** - Unit and integration tests for AI system
5. **Optimize AI response quality** - Fine-tune prompts and error handling
6. **Implement conversation persistence** - Database storage for history

### Known Issues & Solutions
- **Ollama connection failures**: Enhanced error handling implemented, service setup needed
- **TokenData authentication**: Fixed 'id' vs 'user_id' attribute access
- **Database enum validation**: Fixed ProductStatus and ProductCondition alignment
- **Requirements files**: backend/requirements-dev.txt is empty and needs population

## Testing Strategy

### Backend Testing
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app                # Run with coverage (configured in pyproject.toml)
pytest tests/api/               # Run API tests only
pytest tests/agents/            # Run AI agent tests
pytest -v --tb=short           # Verbose with short traceback
tox                            # Run tests in multiple environments
```

### Test Structure
- `tests/api/`: API endpoint integration tests
- `tests/agents/`: AI agent unit tests with mocked APIs
- `tests/services/`: Service layer business logic tests
- `conftest.py`: Shared fixtures and test configuration

## Environment Setup

### Backend Environment Variables
Required in `backend/.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/adogent
GROQ_API_KEY=your_groq_api_key
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000"]
```

### Frontend Environment Variables
Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

## Key Development Notes

### FastAPI Sync vs Async Guidelines
**Important**: FastAPI intelligently handles both sync (`def`) and async (`async def`) functions. You don't need to make everything async!

#### When to use `async def`:
- When using libraries that support `await` (httpx, asyncpg, aiofiles)
- For I/O-bound operations that can benefit from concurrency
- When handling multiple concurrent database queries or API calls
- Example: `async def get_user(user_id: int): user = await db.fetch_user(user_id)`

#### When to use regular `def`:
- For simple operations without I/O
- When using sync-only libraries (requests, psycopg2)
- For CPU-bound operations
- When unsure - **FastAPI's advice: "If you don't know, use normal `def`"**
- Example: `def calculate_total(items: List[Item]): return sum(item.price for item in items)`

FastAPI automatically runs sync functions in a thread pool, preventing blocking. You can mix both types in the same application without performance concerns.

### AI Integration
1. All AI agents inherit from BaseAgent with consistent interfaces
2. Groq client can use async/await for non-blocking operations when beneficial
3. Conversation history managed in-memory (database persistence pending)
4. Health checks and statistics available at `/ai/health` and `/ai/statistics`

### Database Operations
1. **FastAPI handles both sync and async**: Use `async def` with `await` for database queries when using async drivers (asyncpg), or regular `def` with sync drivers
2. **When to use async**: For endpoints with multiple I/O operations or when expecting high concurrency
3. **When sync is fine**: Simple CRUD operations, single database queries, or when using sync-only libraries
4. UUID4 primary keys for all models
5. Soft delete functionality built into BaseModel
6. Automatic timestamps (created_at, updated_at)
7. Enum types must match database definitions exactly

### API Design
1. RESTful endpoints with comprehensive Pydantic schemas
2. Consistent error handling with proper HTTP status codes
3. Pagination support using limit/offset patterns
4. Authentication via Bearer tokens in Authorization header

### Common Tasks

#### Adding a New AI Agent
1. Create agent class in `backend/app/agents/` inheriting from BaseAgent
2. Implement required methods: `process_message()`, `get_capabilities()`
3. Register in `backend/app/services/ai_service.py`
4. Add corresponding API endpoint in `backend/app/api/ai_routes.py`
5. Write tests in `backend/tests/agents/`

#### Creating API Endpoints
1. Add route handler in `backend/app/api/`
2. Create request/response schemas in `backend/app/schemas/`
3. Implement service logic in `backend/app/services/`
4. Add integration tests in `backend/tests/api/`
5. Update OpenAPI documentation

#### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Add new model"
alembic upgrade head  # Apply migration
alembic downgrade -1  # Rollback one migration
```

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check DATABASE_URL format and PostgreSQL is running
2. **Import errors**: Ensure all dependencies installed and PYTHONPATH is correct
3. **Sync/Async mixing**: FastAPI handles both - use async for I/O operations with async libraries, sync is fine otherwise
4. **CORS errors**: Check CORS_ORIGINS in backend/.env includes frontend URL
5. **Empty requirements-dev.txt**: Manually install dependencies listed above

### Database Reset
```bash
cd backend
docker-compose down -v  # Remove volumes
docker-compose up -d postgres
alembic upgrade head
```

## Important Technical Debt
1. Fix empty requirements-dev.txt file
2. Implement proper requirements.txt with all dependencies
3. Complete Ollama service setup for multimodal support
4. Add database indexes for search optimization
5. Implement API rate limiting
6. Add conversation persistence to database
7. Create database backup procedures

## Production Deployment Notes
- Backend is deployed at https://adogent.onrender.com
- Use environment-specific configuration
- Enable structured JSON logging
- Configure connection pooling for PostgreSQL
- Set up monitoring and alerting
- Implement proper error tracking