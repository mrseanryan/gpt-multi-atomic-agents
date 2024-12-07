# so future errors halt the script.
set -e

echo Formatting ...
ruff format

echo "Linting [with fix]..."
ruff check . --fix

echo [done]
