# PyCaldera Development Guide

## Build & Test Commands
- Install dev dependencies: `pip install -r requirements-dev.txt`
- Run all tests: `pytest tests/`
- Run a single test: `pytest tests/test_async_client.py::test_set_temperature`
- Run with coverage: `pytest --cov=pycaldera tests/`
- Build package: `python -m build`
- Install pre-commit hooks: `pre-commit install`

## Code Style
- **Formatting**: Black with 88 character line length
- **Imports**: isort with sections E, F, W, I001
- **Type Checking**: mypy with full annotations
- **Linting**: ruff, pylint
- **Docstrings**: Google style with full parameter descriptions
- **Naming**: snake_case for variables/functions, PascalCase for classes, ALL_CAPS for constants
- **Error Handling**: Custom exceptions in exceptions.py, catch specific exceptions
- **Testing**: pytest with async support (pytest-asyncio)
- **Async Pattern**: All API methods are async with proper context manager support

## File Organization
- Core client in async_client.py
- Data models using pydantic in models.py
- Exceptions in exceptions.py
