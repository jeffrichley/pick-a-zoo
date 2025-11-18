# Development tasks for pick-a-zoo

# Set shell based on OS for cross-platform compatibility
# Windows uses PowerShell, Unix-like systems use sh
set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
set shell := ["sh", "-cu"]

prelude := '''
# Your one-time pre-hook
echo "🔧 Checking dev dependencies..."
uv sync --dev --quiet
'''

# Run tests
test:
    uv run pytest tests

# Run linting
lint:
    uv run ruff check src tests

# Run type checking
type-check:
    uv run mypy src

# Run all checks (lint, type-check, test)
check: lint type-check test
    @echo "All checks passed!"
