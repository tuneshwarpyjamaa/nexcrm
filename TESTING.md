# Testing Documentation

## Overview

This document provides comprehensive information about the testing strategy, test suites, and how to run tests for the NexCRM application.

## Test Structure

### Test Categories

1. **Unit Tests** (`tests/test_*.py`)
   - Individual component testing
   - Mocked dependencies
   - Fast execution

2. **Integration Tests** (`tests/test_integration.py`)
   - End-to-end workflows
   - Cross-module interactions
   - Realistic scenarios

3. **Performance Tests** (`tests/test_performance.py`)
   - Load testing
   - Concurrent request handling
   - Response time validation

4. **Security Tests** (Part of CI/CD pipeline)
   - Vulnerability scanning
   - Dependency checking
   - Code security analysis

### Test Files

- `tests/conftest.py` - Test configuration and fixtures
- `tests/test_auth.py` - Authentication and authorization tests
- `tests/test_contacts.py` - Contact management tests
- `tests/test_deals.py` - Deal management tests
- `tests/test_tasks.py` - Task management tests
- `tests/test_notes.py` - Note management tests
- `tests/test_emails.py` - Email functionality tests
- `tests/test_activity.py` - Activity tracking tests
- `tests/test_settings.py` - User settings tests
- `tests/test_subscriptions.py` - Subscription management tests
- `tests/test_integration.py` - Integration workflow tests
- `tests/test_performance.py` - Performance and load tests
- `backend/tests/performance_test.py` - Locust performance testing

## Running Tests

### Local Development

#### Prerequisites
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set up test database (optional, uses mocks by default)
export DATABASE_URL="postgresql://user:password@localhost/testdb"
```

#### Run All Tests
```bash
cd backend
pytest tests/ -v
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/ -m "unit" -v

# Integration tests only
pytest tests/test_integration.py -v

# Performance tests only
pytest tests/test_performance.py -v

# Authentication tests only
pytest tests/test_auth.py -v
```

#### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

#### Run Linting and Formatting
```bash
cd backend
flake8 .
black --check .
isort --check-only .
```

### Performance Testing

#### Using Locust
```bash
cd backend
locust --headless --users 50 --spawn-rate 5 --run-time 60s --host http://localhost:8000 -f tests/performance_test.py
```

#### Performance Test Scenarios
- **Normal Load**: 50 users over 10 minutes
- **Peak Load**: 100 users over 5 minutes  
- **Stress Test**: 200 users over 15 minutes
- **Endurance Test**: 25 users over 1 hour

### Security Testing

#### Run Security Scans
```bash
cd backend

# Bandit security linter
bandit -r . -f json -o bandit-report.json

# Safety dependency checker
safety check --json --output safety-report.json

# Semgrep static analysis
semgrep --config=auto --json --output=semgrep-report.json .

# Pip audit for vulnerabilities
pip-audit --format=json --output=audit-report.json
```

## Test Configuration

### Environment Variables for Testing
```bash
# Required for authentication tests
SECRET_KEY=test-secret-key-for-testing

# Database configuration (if not using mocks)
DATABASE_URL=postgresql://testuser:testpassword@localhost:5432/testdb

# Other test environment variables
PYTHONPATH=./backend
```

### pytest Configuration

Configuration is defined in `pyproject.toml`:

- Test discovery patterns
- Coverage settings
- Markers for different test categories
- Asyncio configuration

### Mocking Strategy

Tests use extensive mocking to:
- Isolate units under test
- Ensure consistent test results
- Avoid external dependencies
- Improve test execution speed

Key mock patterns:
```python
# Database operations
mock_db.fetch = AsyncMock(return_value=[...])
mock_db.fetchrow = AsyncMock(return_value={...})
mock_db.execute = AsyncMock(return_value=None)

# Authentication
mock_token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm="HS256")
```

## CI/CD Pipeline

### GitHub Actions Workflow

The pipeline includes:

1. **Backend Tests**
   - Unit tests with coverage
   - Integration tests
   - Linting and formatting checks

2. **Frontend Tests**
   - Unit tests
   - Linting
   - Build verification

3. **Performance Tests**
   - Load testing with Locust
   - Response time validation

4. **Security Tests**
   - Code security scanning
   - Dependency vulnerability checks
   - Static analysis

5. **Database Tests**
   - Migration testing
   - Connection validation

6. **Deployment**
   - Docker image building
   - Container registry push
   - Staging deployment (main branch only)

### Pipeline Triggers

- **Push** to `main` or `develop` branches
- **Pull Requests** to `main` or `develop` branches

## Test Data Management

### Fixtures

Common test fixtures are defined in `conftest.py`:

- `client` - HTTP client for API testing
- `mock_db` - Database connection mock
- `event_loop` - Asyncio event loop

### Test Data Patterns

```python
# Sample contact data
contact_data = {
    "name": "Test Contact",
    "email": "test@example.com",
    "phone": "+1234567890",
    "company": "Test Corp"
}

# Sample deal data
deal_data = {
    "title": "Test Deal",
    "value": 10000.0,
    "status": "open",
    "contact_id": "c_123"
}
```

## Best Practices

### Writing Tests

1. **Arrange, Act, Assert Pattern**
   ```python
   # Arrange
   mock_db.fetchrow = AsyncMock(return_value={...})
   
   # Act
   response = await client.post("/api/contacts", json=data, headers=headers)
   
   # Assert
   assert response.status_code == 200
   ```

2. **Descriptive Test Names**
   ```python
   async def test_create_contact_with_valid_data(client, mock_db):
   async def test_create_contact_with_invalid_email(client, mock_db):
   ```

3. **Test Edge Cases**
   - Invalid input data
   - Missing required fields
   - Unauthorized access
   - Database errors

4. **Use Markers Appropriately**
   ```python
   @pytest.mark.integration
   @pytest.mark.slow
   @pytest.mark.auth
   ```

### Mocking Guidelines

1. **Mock External Dependencies**
   - Database connections
   - External APIs
   - File system operations

2. **Configure Mocks per Test**
   - Avoid shared state between tests
   - Reset mocks in `tearDown` if needed

3. **Verify Mock Calls**
   ```python
   mock_db.execute.assert_called_once()
   assert "INSERT INTO contacts" in mock_db.execute.call_args[0][0]
   ```

### Performance Considerations

1. **Use Efficient Test Data**
   - Small, focused datasets
   - Reusable fixtures

2. **Parallel Test Execution**
   - Tests should be independent
   - Avoid shared resources

3. **Mock Slow Operations**
   - Network calls
   - Database queries
   - File I/O

## Troubleshooting

### Common Issues

1. **Async Test Failures**
   ```bash
   # Ensure asyncio mode is set
   pytest --asyncio-mode=auto
   ```

2. **Import Errors**
   ```bash
   # Set Python path
   export PYTHONPATH=./backend
   ```

3. **Database Connection Issues**
   - Check mock configuration
   - Verify environment variables

4. **Coverage Reporting**
   ```bash
   # Install coverage dependencies
   pip install pytest-cov
   ```

### Debugging Tests

1. **Verbose Output**
   ```bash
   pytest -v -s tests/test_specific.py
   ```

2. **Stop on First Failure**
   ```bash
   pytest -x tests/
   ```

3. **Run Specific Test**
   ```bash
   pytest tests/test_auth.py::test_login_valid_credentials -v
   ```

4. **Debug with pdb**
   ```bash
   pytest --pdb tests/test_specific.py
   ```

## Coverage Goals

- **Overall Coverage**: > 80%
- **Critical Paths**: > 90%
- **Authentication**: > 95%
- **Database Operations**: > 85%

Coverage reports are generated in:
- HTML: `htmlcov/index.html`
- XML: `coverage.xml`
- Terminal: Direct output

## Continuous Improvement

1. **Regular Test Reviews**
   - Remove obsolete tests
   - Update test data
   - Improve assertions

2. **Performance Monitoring**
   - Track test execution time
   - Identify slow tests
   - Optimize where needed

3. **Coverage Maintenance**
   - Review uncovered code
   - Add tests for new features
   - Maintain coverage thresholds

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
