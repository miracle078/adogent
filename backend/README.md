# AI-Powered E-Commerce MVP

Minimal FastAPI e-commerce platform with AI agents, knowledge graph user profiles, and Groq LLM integration.

## Stack
- FastAPI (Python 3.11+) with async endpoints
- Groq API for LLM interactions  
- AWS Neptune for user profile knowledge graph
- SQLAlchemy (async) + Alembic for relational data
- Docker Compose + AWS ECS/EKS deployment

## Quick Start
```bash
docker-compose up --build
```

## Project Structure
```
├── app/                    # Core application
│   ├── api/               # FastAPI routers
│   ├── services/          # Business logic layer
│   ├── agents/            # AI agents for LLM interactions
│   ├── db/                # Database models & connections
│   ├── schemas/           # Pydantic models
│   └── utils/             # Shared utilities
├── infrastructure/        # AWS & deployment configs
├── tests/                 # Test suite
├── alembic/              # Database migrations
├── .github/              # CI/CD workflows
└── docker/               # Container configs
``` MVP

Minimal FastAPI e-commerce platform with AI agents, knowledge graph user profiles, and Groq LLM integration.

## Stack
- FastAPI (Python 3.11+) with async endpoints
- Groq API for LLM interactions  
- AWS Neptune for user profile knowledge graph
- SQLAlchemy (async) + Alembic for relational data
- Docker Compose + AWS ECS/EKS deployment

## Quick Start
```bash
docker-compose up --build
```
