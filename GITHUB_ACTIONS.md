# GitHub Actions CI/CD Setup

This document explains the GitHub Actions workflow for the NexCRM project.

## 🚀 Pipeline Overview

The CI/CD pipeline includes the following jobs:

### 1. Backend Tests
- **Environment**: Ubuntu with Python 3.11
- **Database**: PostgreSQL 15 + Redis 7
- **Steps**:
  - Install dependencies
  - Run database migrations
  - Code linting (flake8, black, isort)
  - Basic CI tests (test_ci_basic.py)
  - Full unit tests with coverage
  - Integration tests
  - Upload coverage to Codecov

### 2. Frontend Tests
- **Environment**: Ubuntu with Node.js 18
- **Steps**:
  - Install dependencies
  - Run linting
  - Run unit tests
  - Build frontend

### 3. Performance Tests
- **Tools**: Locust for load testing
- **Tests**: Concurrent API request handling

### 4. Security Tests
- **Tools**: Bandit, Safety, Semgrep, pip-audit
- **Checks**: Security vulnerabilities, code analysis

### 5. Database Tests
- **Tests**: Migration integrity, connection handling

### 6. Deploy (main branch only)
- **Steps**: Docker build, deployment to staging

## 🔧 Key Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key for testing
- `PYTHONPATH`: Backend module path

### Test Strategy
1. **Basic CI Tests**: Core functionality verification
2. **Unit Tests**: Comprehensive module testing
3. **Integration Tests**: End-to-end workflows
4. **Error Handling**: Tests continue on failure with `|| true`

### Coverage
- **Source**: Backend code only
- **Reports**: XML + HTML formats
- **Upload**: Codecov integration

## 🛠️ Troubleshooting

### Common Issues
1. **Import Errors**: Check PYTHONPATH configuration
2. **Database Connection**: Verify PostgreSQL service health
3. **Test Failures**: Check environment variables
4. **Coverage Issues**: Ensure source path is correct

### Debugging Steps
1. Check GitHub Actions logs
2. Run tests locally with same environment
3. Verify database migrations
4. Check dependency versions

## 📋 Test Files

### Core Test Files
- `tests/test_ci_basic.py`: Basic CI verification
- `tests/test_auth.py`: Authentication tests
- `tests/test_contacts.py`: Contact management
- `tests/test_deals.py`: Deal management
- `tests/test_tasks.py`: Task management
- `tests/test_notes.py`: Note management
- `tests/test_subscriptions.py`: Subscription management

### Test Configuration
- `pyproject.toml`: pytest configuration
- `conftest.py`: Common test fixtures
- `requirements.txt`: Test dependencies

## 🚦 Pipeline Status

### Success Indicators
- ✅ All basic CI tests pass
- ✅ Code linting passes
- ✅ Unit tests pass
- ✅ Coverage uploaded
- ✅ Security scans complete

### Failure Handling
- Tests continue on non-critical failures
- Security scans generate warnings but don't fail pipeline
- Coverage upload is non-blocking

## 🔄 Continuous Integration

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### Deployment
- Automatic deployment on successful pipeline to `main`
- Staging deployment for testing

## 📊 Monitoring

### Metrics
- Test execution time
- Coverage percentage
- Security scan results
- Performance benchmarks

### Alerts
- Pipeline failure notifications
- Security vulnerability alerts
- Performance degradation alerts
