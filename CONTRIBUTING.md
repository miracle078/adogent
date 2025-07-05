<h1 align="center">🧐 Contributing Docs</h1>
<p align="center">If you would like to make a contribution, whether it's updating the README, adding a new feature, fixing a bug, or performing a chore, please follow these steps:
    <br> 
</p>

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- **Python 3.11+** installed
- **Docker & Docker Compose** installed
- **Git** configured with your credentials
- **Groq API Key** for testing AI features

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/thegoldenage.git
   cd thegoldenage
   ```

## 🌿 Branch Management

### Create a New Branch

Before starting work, create a new branch off the main branch. Use the following naming convention:

- For features: `feat/descriptive-name`
- For fixes: `fix/descriptive-name`
- For chores: `chore/descriptive-name`

**Example:** To create a new branch for a feature called "add user authentication":

```bash
git checkout -b feat/add-user-authentication
```

This will create a new branch and switch to it.

### Branch Guidelines

- Keep branches focused on a single feature or fix
- Use descriptive names that explain the purpose
- Regularly sync with main branch to avoid conflicts
- Delete branches after successful merge

## 💻 Development Workflow

### Setup Development Environment

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements-dev.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development services:**
   ```bash
   docker-compose up -d
   ```

### Make Your Changes

Work on your changes, whether it's:
- Updating documentation
- Adding new features
- Fixing bugs
- Performing maintenance tasks

### Code Standards

- **Follow PEP 8** style guidelines
- **Use type hints** for all functions
- **Write comprehensive docstrings** for classes and functions
- **Maintain test coverage** above 85%
- **Use async/await** for all database operations
- **Follow the service layer pattern** - keep business logic in services, not routers

### Testing

Before submitting your changes:

1. **Run tests:**
   ```bash
   cd backend
   pytest
   ```

2. **Check code quality:**
   ```bash
   black app/
   ruff check app/
   mypy app/
   ```

3. **Test API endpoints:**
   ```bash
   # Start the server
   uvicorn app.main:app --reload
   
   # Access API docs
   open http://localhost:8000/docs
   ```

## 📝 Commit Guidelines

### Commit Message Format

Use the following format for your commit messages:

```bash
git add .
git commit -m "feat(auth): add user authentication"
```

The commit message format follows conventional commits:

```
type(scope): short description

Longer description of the changes, if necessary.
```

### Commit Types

- `feat`: A new feature
- `fix`: A bug fix
- `chore`: Maintenance tasks (updating dependencies, etc.)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `ci`: Changes to CI/CD pipeline

### Commit Scope

The scope indicates the area of the codebase affected:
- `auth`: Authentication and authorization
- `api`: API endpoints and routing
- `agents`: AI agent implementations
- `db`: Database models and migrations
- `services`: Business logic services
- `tests`: Test files
- `docs`: Documentation
- `config`: Configuration files

### Examples

```bash
git commit -m "feat(agents): add product recommendation agent"
git commit -m "fix(auth): resolve JWT token validation issue"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(api): add integration tests for order endpoints"
```

## 🔄 Pull Request Process

### Push Your Changes

Push your branch to your fork:

```bash
git push origin feat/add-user-authentication
```

### Create a Pull Request

1. **Navigate to the original repository** on GitHub
2. **Click "New Pull Request"**
3. **Select your branch** from your fork
4. **Fill out the PR template** with:
   - Clear description of changes
   - Link to related issues
   - Testing instructions
   - Screenshots (if applicable)

### PR Requirements

Before your PR can be merged:

- [ ] All tests pass
- [ ] Code follows project standards
- [ ] Documentation is updated (if needed)
- [ ] CHANGELOG.md is updated (for significant changes)
- [ ] PR has been reviewed by maintainers
- [ ] All feedback has been addressed

### Review Process

1. **Automated checks** will run (CI/CD pipeline)
2. **Maintainers will review** your code
3. **Address feedback** by making additional commits
4. **Approval and merge** once all requirements are met

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment details** (OS, Python version, etc.)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error messages** and stack traces
- **Minimal code example** (if applicable)

## 💡 Feature Requests

When requesting features:

- **Describe the problem** you're trying to solve
- **Explain your proposed solution**
- **Provide use cases** and examples
- **Consider implementation complexity**
- **Link to related issues** or discussions

## 📚 Documentation

### Documentation Types

- **API Documentation**: Automatically generated from code
- **User Guides**: Step-by-step instructions for users
- **Developer Docs**: Technical implementation details
- **Contributing Guide**: This document

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting
- Include diagrams for complex concepts

## 🔒 Security

### Reporting Security Issues

- **Do not** open public issues for security vulnerabilities
- **Email security concerns** to [security@thegoldenage.com](mailto:security@thegoldenage.com)
- **Include detailed information** about the vulnerability
- **Allow time** for the issue to be addressed before public disclosure

### Security Guidelines

- Never commit sensitive information (API keys, passwords, etc.)
- Use environment variables for configuration
- Follow security best practices for API development
- Keep dependencies updated

## 🙏 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Being respectful and inclusive
- Giving and receiving constructive feedback
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Harassment, discrimination, or trolling
- Publishing private information without consent
- Inappropriate comments or personal attacks
- Any other unprofessional conduct

### Enforcement

Report unacceptable behavior to the project maintainers. All complaints will be reviewed and investigated fairly.

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Email**: [team@thegoldenage.com](mailto:team@thegoldenage.com)

### Before Asking for Help

1. Check existing issues and documentation
2. Search previous discussions
3. Try to reproduce the issue
4. Prepare a minimal example

---

<div align="center">

**Thank you for your contribution! 🎈**

Every contribution, no matter how small, helps make The Golden Age better.

**[⬆ Back to Top](#top)**

</div>
