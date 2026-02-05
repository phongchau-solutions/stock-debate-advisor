# Contributing to Stock Debate Advisor v8

Thank you for your interest in contributing to Stock Debate Advisor v8! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/stock-debate-advisor.git
   cd stock-debate-advisor/v8
   ```
3. **Set up your development environment** (see [GETTING_STARTED.md](./docs/GETTING_STARTED.md))
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Choose an Issue

- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it
- Ask questions if anything is unclear

### 2. Make Your Changes

- Keep changes focused and atomic
- Follow the existing code style
- Write meaningful commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
just test

# Run specific tests
cd apps/frontend && pnpm test
cd services/debate-service && poetry run pytest
```

### 4. Submit a Pull Request

- Push your changes to your fork
- Open a Pull Request against the `develop` branch
- Fill out the PR template completely
- Link related issues

## Coding Standards

### TypeScript/JavaScript (Frontend)

- Use TypeScript for type safety
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components and hooks in React
- Prefer named exports over default exports
- Use absolute imports with path aliases

**Example:**
```typescript
// Good
import { Button } from '@/components/common/Button';
import { useDebates } from '@/hooks/useDebates';

export const DebateList: React.FC<Props> = ({ userId }) => {
  const { debates, loading } = useDebates(userId);
  
  if (loading) return <Spinner />;
  
  return (
    <div className="space-y-4">
      {debates.map(debate => (
        <DebateCard key={debate.id} debate={debate} />
      ))}
    </div>
  );
};
```

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all functions
- Use async/await for I/O operations
- Keep functions small and focused
- Use Pydantic for data validation

**Example:**
```python
# Good
from typing import List
from fastapi import APIRouter, Depends
from app.schemas.debate import DebateCreate, DebateResponse
from app.crud.debate import debate_crud

router = APIRouter()

@router.post("/debates", response_model=DebateResponse)
async def create_debate(
    debate_in: DebateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DebateResponse:
    """Create a new debate."""
    debate = await debate_crud.create(
        db=db,
        object={"user_id": current_user.id, **debate_in.model_dump()}
    )
    return debate
```

### Formatting

**Frontend:**
```bash
# Format code
pnpm format

# Check formatting
pnpm lint
```

**Backend:**
```bash
# Format code
poetry run black .
poetry run isort .

# Check formatting
poetry run black --check .
poetry run flake8
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(debate): add real-time status updates via WebSocket"

# Bug fix
git commit -m "fix(auth): resolve token expiration issue"

# Documentation
git commit -m "docs(api): add API endpoint documentation"

# Refactor
git commit -m "refactor(data-service): extract stock fetcher to separate module"

# Multiple changes
git commit -m "feat(frontend): add debate history page

- Add DebateHistory component
- Implement pagination
- Add filters for status and date
- Update navigation menu

Closes #123"
```

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally (`just test`)
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commits follow conventional commit format
- [ ] No merge conflicts with target branch

### PR Template

When creating a PR, include:

1. **Description**: What does this PR do?
2. **Related Issues**: Link to related issues
3. **Type of Change**: Feature, bug fix, etc.
4. **Testing**: How was this tested?
5. **Screenshots**: For UI changes
6. **Checklist**: Complete the PR checklist

### Review Process

1. **Automated Checks**: CI/CD pipeline must pass
2. **Code Review**: At least one approval required
3. **Testing**: Reviewer may test locally
4. **Merge**: Maintainer will merge after approval

## Testing Guidelines

### Frontend Tests

**Unit Tests (Vitest):**
```typescript
import { render, screen } from '@testing-library/react';
import { DebateCard } from './DebateCard';

describe('DebateCard', () => {
  it('displays debate symbol', () => {
    const debate = { id: '1', symbol: 'AAPL', status: 'COMPLETED' };
    render(<DebateCard debate={debate} />);
    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });
});
```

**Integration Tests (Playwright):**
```typescript
test('create debate flow', async ({ page }) => {
  await page.goto('/debates/new');
  await page.fill('[name="symbol"]', 'AAPL');
  await page.click('button[type="submit"]');
  await expect(page.locator('.debate-status')).toContainText('INITIATED');
});
```

### Backend Tests

**Unit Tests (pytest):**
```python
import pytest
from app.crud.debate import debate_crud

@pytest.mark.asyncio
async def test_create_debate(db_session):
    """Test debate creation."""
    debate_data = {
        "symbol": "AAPL",
        "rounds": 3,
        "user_id": "test_user"
    }
    debate = await debate_crud.create(db=db_session, object=debate_data)
    assert debate.symbol == "AAPL"
    assert debate.status == "INITIATED"
```

**Integration Tests:**
```python
@pytest.mark.asyncio
async def test_debate_api_flow(client):
    """Test complete debate API flow."""
    # Create debate
    response = await client.post(
        "/api/v1/debates",
        json={"symbol": "AAPL", "rounds": 3}
    )
    assert response.status_code == 201
    debate_id = response.json()["id"]
    
    # Get debate status
    response = await client.get(f"/api/v1/debates/{debate_id}")
    assert response.status_code == 200
```

### Test Coverage

- **Target**: 80% code coverage
- **Required**: All new features must have tests
- **Run coverage**: 
  - Frontend: `pnpm test -- --coverage`
  - Backend: `poetry run pytest --cov=app`

## Documentation

### Code Documentation

**TypeScript:**
```typescript
/**
 * Creates a new debate for the specified stock symbol.
 * 
 * @param symbol - Stock symbol (e.g., 'AAPL')
 * @param rounds - Number of debate rounds (1-10)
 * @returns Promise resolving to the created debate
 * @throws Error if symbol is invalid or service is unavailable
 */
export async function createDebate(
  symbol: string,
  rounds: number
): Promise<Debate> {
  // Implementation
}
```

**Python:**
```python
async def create_debate(
    symbol: str,
    rounds: int,
    user_id: str
) -> Debate:
    """
    Create a new debate for the specified stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        rounds: Number of debate rounds (1-10)
        user_id: ID of the user creating the debate
        
    Returns:
        The created debate object
        
    Raises:
        ValueError: If symbol is invalid
        DatabaseError: If database operation fails
    """
    # Implementation
```

### README Updates

When adding new features:
- Update relevant README files
- Add usage examples
- Update architecture diagrams if needed
- Document new environment variables

### API Documentation

- FastAPI generates automatic docs at `/docs`
- Keep OpenAPI schemas up to date
- Document all endpoints, parameters, and responses
- Include example requests and responses

## Questions?

- Check existing documentation in `docs/`
- Search for similar issues on GitHub
- Ask in pull request comments
- Create a discussion on GitHub

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Eligible for maintainer status based on contributions

Thank you for contributing to Stock Debate Advisor v8! 🚀
