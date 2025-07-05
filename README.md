<p align="center">
  <a href="" rel="noopener">
 <img src="https://i.imgur.com/AZ2iWek.png" alt="Adogent Logo"></a>
</p>
<h3 align="center"> ADOGENT - AI-Powered E-Commerce Platform</h3>

<div align="center">

[![Hackathon](https://img.shields.io/badge/hackathon-Agent--Powered--E--Commerce-orange.svg)](https://github.com/miracle078/adogent)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/miracle078/adogent.svg)](https://github.com/miracle078/adogent/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/miracle078/adogent.svg)](https://github.com/miracle078/adogent/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB.svg?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6.svg?logo=typescript)](https://typescriptlang.org)

</div>

---

<p align="center">
An intelligent luxury e-commerce platform powered by AI agents that provides personalized shopping experiences through natural language conversations and voice-first interfaces.
</p>

## 📝 Table of Contents

- [About](#about)
- [Features](#features)
- [Technology Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [AI Agents](#ai-agents)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🚀 About <a name="about"></a>

**ADOGENT** is a cutting-edge AI-powered e-commerce platform that revolutionizes online shopping through intelligent agent interactions. Built for modern consumers who demand personalized, conversational, and intuitive shopping experiences.

### 🎯 Key Highlights

- **🤖 AI Shopping Assistants**: Groq-powered agents for intelligent product discovery
- **🎙️ Voice-First Interface**: Natural language shopping through voice and text
- **🛍️ Luxury Commerce**: Premium shopping experience with personalized recommendations
- **⚡ Ultra-Fast Responses**: Sub-second AI interactions using Groq's lightning-fast LLM API
- **🔐 Secure & Scalable**: Enterprise-grade security with AWS cloud infrastructure

## ✨ Features <a name="features"></a>

### 🛍️ Core E-Commerce Features
- **Product Catalog**: Comprehensive inventory with new and second-hand items
- **Smart Search**: AI-powered product discovery with natural language queries
- **User Profiles**: Dynamic user profiling through conversation analysis
- **Order Management**: Complete order lifecycle from cart to delivery
- **Secure Payments**: Safe and encrypted payment processing

### 🤖 AI-Powered Features
- **Conversational Shopping**: Chat naturally with AI agents to find products
- **Voice Commerce**: Shop hands-free using voice commands
- **Personalized Recommendations**: ML-driven product suggestions
- **Intent Recognition**: Advanced NLP for understanding user needs
- **Context Awareness**: Maintain conversation history across sessions

### 🎨 User Experience
- **Luxury Design**: Premium UI with dark mode and elegant animations
- **Responsive Interface**: Seamless experience across all devices
- **Accessibility**: Voice-first design ensures inclusive access
- **Real-time Updates**: Live order tracking and notifications

## ⚡ Technology Stack <a name="tech-stack"></a>

### 🖥️ Frontend
- **[React 18](https://reactjs.org/)** - Modern UI library with hooks and concurrent features
- **[TypeScript](https://typescriptlang.org/)** - Type-safe JavaScript for better development
- **[Vite](https://vitejs.dev/)** - Lightning-fast build tool and dev server
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[shadcn/ui](https://ui.shadcn.com/)** - Beautiful and accessible React components
- **[React Router](https://reactrouter.com/)** - Declarative routing for React
- **[TanStack Query](https://tanstack.com/query)** - Powerful data synchronization

### 🔧 Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[SQLAlchemy](https://sqlalchemy.org/)** - Async ORM for database operations
- **[PostgreSQL](https://postgresql.org/)** - Robust relational database
- **[Redis](https://redis.io/)** - In-memory caching and session storage
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration management
- **[Pydantic](https://pydantic.dev/)** - Data validation using Python type hints

### 🤖 AI & ML
- **[Groq](https://groq.com/)** - Ultra-fast LLM API for AI agents
- **Custom AI Agents** - Specialized agents for different e-commerce functions
- **Natural Language Processing** - Advanced text and speech processing
- **Machine Learning Models** - Recommendation algorithms and user profiling

### ☁️ Infrastructure
- **[Docker](https://docker.com/)** - Containerization for consistent deployments
- **[AWS ECS](https://aws.amazon.com/ecs/)** - Container orchestration
- **[AWS RDS](https://aws.amazon.com/rds/)** - Managed database service
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD automation

## 📂 Project Structure <a name="project-structure"></a>

```
adogent/
├── 📱 Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Application pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Utility functions
│   │   └── assets/           # Static assets
│   ├── public/               # Public static files
│   ├── package.json          # Node.js dependencies
│   └── vite.config.ts        # Vite configuration
│
├── 🔧 Backend (Python/FastAPI)
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   ├── agents/           # AI agent implementations
│   │   ├── services/         # Business logic layer
│   │   ├── db/               # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── utils/            # Shared utilities
│   ├── tests/                # Test suite
│   ├── docker/               # Docker configurations
│   ├── requirements.txt      # Python dependencies
│   └── pyproject.toml        # Python project config
│
├── 🚀 Infrastructure
│   ├── .github/workflows/    # CI/CD pipelines
│   ├── docker-compose.yml    # Development environment
│   └── infrastructure/       # AWS configurations
│
└── 📚 Documentation
    ├── README.md             # This file
    ├── CONTRIBUTING.md       # Contribution guidelines
    └── docs/                 # Additional documentation
```

## 🚀 Getting Started <a name="getting-started"></a>

### Prerequisites

- **Node.js 18+** - [Install with nvm](https://github.com/nvm-sh/nvm)
- **Python 3.11+** - [Download Python](https://python.org/downloads/)
- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Groq API Key** - [Get your API key](https://console.groq.com/keys)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/miracle078/adogent.git
   cd adogent
   ```

2. **Frontend Development**
   ```bash
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   
   # Access at http://localhost:8080
   ```

3. **Backend Development**
   ```bash
   # Navigate to backend
   cd backend
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start backend server
   uvicorn app.main:app --reload
   
   # Access API docs at http://localhost:8000/docs
   ```

4. **Full Stack with Docker**
   ```bash
   # Start all services
   docker-compose up --build
   
   # Frontend: http://localhost:8080
   # Backend: http://localhost:8000
   # API Docs: http://localhost:8000/docs
   ```

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/adogent
REDIS_URL=redis://localhost:6379

# AI Services
GROQ_API_KEY=your_groq_api_key

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# AWS (for production)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

## 🎯 Usage <a name="usage"></a>

### Frontend Interface

The React frontend provides a modern, responsive interface for:

- **Product Browsing**: Explore products with advanced filtering
- **Voice Shopping**: Use voice commands to search and shop
- **AI Chat**: Converse with shopping assistants
- **User Dashboard**: Manage orders and preferences

### API Endpoints

The FastAPI backend exposes RESTful APIs:

```bash
# Authentication
POST /api/auth/register      # User registration
POST /api/auth/login         # User login
POST /api/auth/logout        # User logout

# Products
GET  /api/products           # Browse products
POST /api/products/search    # Search products
GET  /api/products/{id}      # Product details

# AI Agents
POST /api/agents/chat        # Chat with AI assistant
POST /api/agents/voice       # Voice interactions
GET  /api/agents/recommendations  # Get recommendations

# Orders
POST /api/orders             # Create order
GET  /api/orders/{id}        # Order details
GET  /api/orders/history     # Order history
```

### Voice Commands

Interact naturally with the platform:

```
"Show me laptops under $1000"
"Find wireless headphones with good reviews"
"What would you recommend for a student?"
"Add the MacBook Pro to my cart"
"What's the status of my order?"
```

## 🤖 AI Agents <a name="ai-agents"></a>

ADOGENT features specialized AI agents powered by Groq's ultra-fast LLM API:

### 🛍️ Product Agent
- **Product Discovery**: Find products based on natural language queries
- **Specification Matching**: Match products to user requirements
- **Price Analysis**: Compare prices and suggest best deals
- **Inventory Awareness**: Real-time stock information

### 📊 Recommendation Agent
- **Personalized Suggestions**: AI-powered product recommendations
- **Cross-selling**: Suggest complementary products
- **Trend Analysis**: Identify popular and trending items
- **User Behavior Learning**: Adapt recommendations based on interactions

### 🛠️ Support Agent
- **Order Assistance**: Help with order tracking and issues
- **Product Information**: Detailed product specifications
- **Return Processing**: Guide users through returns
- **Technical Support**: Troubleshoot platform issues

### 🎙️ Voice Agent
- **Speech Recognition**: Convert voice input to text
- **Intent Recognition**: Understand user intent from natural language
- **Multimodal Response**: Respond via voice and text
- **Context Awareness**: Maintain conversation context

## 📚 API Documentation <a name="api-documentation"></a>

### Interactive Documentation

Access comprehensive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Authentication

Most endpoints require JWT authentication:

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/protected-endpoint"
```

## 🛠️ Development <a name="development"></a>

### Frontend Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Backend Development

```bash
cd backend

# Install development dependencies
pip install -r requirements-dev.txt

# Format code
black app/

# Lint code
ruff check app/

# Type checking
mypy app/

# Database migrations
alembic upgrade head
```

### Development Commands

```bash
# Frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run lint         # Lint TypeScript/React

# Backend
make dev            # Start development server
make test           # Run tests
make format         # Format code
make lint           # Lint Python code
make migrate        # Run database migrations
```

## 🧪 Testing <a name="testing"></a>

### Frontend Testing

```bash
# Run tests (when configured)
npm test

# Run tests with coverage
npm run test:coverage
```

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/api/test_products.py

# Run with verbose output
pytest -v
```

### Test Structure

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Agent Tests**: Test AI agent functionality with mocked APIs
- **E2E Tests**: Full application flow testing

## 🚀 Deployment <a name="deployment"></a>

### Development Deployment

```bash
# Using Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:8080
# Backend: http://localhost:8000
```

### Production Deployment

#### Option 1: Lovable Platform

1. Connect your repository to [Lovable](https://lovable.dev/projects/2bec7813-1fda-4fbf-9305-50864ec62a2e)
2. Click "Share" → "Publish"
3. Your app will be deployed automatically

#### Option 2: AWS ECS

```bash
# Build and push Docker images
docker build -t adogent-frontend .
docker build -t adogent-backend ./backend

# Deploy using AWS ECS
# (Configure your AWS credentials first)
aws ecs create-service --service-name adogent --cluster production
```

#### Option 3: Vercel (Frontend) + Railway (Backend)

```bash
# Deploy frontend to Vercel
npx vercel --prod

# Deploy backend to Railway
# Connect your GitHub repository to Railway
```

### Environment Configuration

**Production Environment Variables:**

```bash
# Frontend (.env.production)
VITE_API_URL=https://api.adogent.com
VITE_ENVIRONMENT=production

# Backend (production.env)
DATABASE_URL=postgresql://user:pass@prod-db:5432/adogent
REDIS_URL=redis://prod-redis:6379
GROQ_API_KEY=prod_groq_key
JWT_SECRET_KEY=secure-production-secret
```

## 🤝 Contributing <a name="contributing"></a>

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feat/amazing-feature`
3. **Make your changes**: Follow our coding standards
4. **Test your changes**: Ensure all tests pass
5. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
6. **Push to the branch**: `git push origin feat/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow TypeScript/Python best practices
- Write comprehensive tests
- Update documentation
- Follow conventional commit format
- Ensure all CI checks pass

## 📄 License <a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- **[Groq](https://groq.com/)** for ultra-fast LLM API
- **[Lovable](https://lovable.dev/)** for development platform
- **[shadcn/ui](https://ui.shadcn.com/)** for beautiful components
- **[FastAPI](https://fastapi.tiangolo.com/)** for the amazing Python framework

---

<div align="center">

**Built with ❤️ by The Golden Age**

[🔗 Live Demo](https://lovable.dev/projects/2bec7813-1fda-4fbf-9305-50864ec62a2e) • 
[📖 Documentation](docs/) • 
[🐛 Report Bug](https://github.com/miracle078/adogent/issues) • 
[✨ Request Feature](https://github.com/miracle078/adogent/issues)

**⭐ Star us on GitHub if this project helped you!**

</div>
