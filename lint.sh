# so future errors halt the script.
set -e

echo Formatting ...
ruff format

echo Linting ...
ruff check .

echo [done]
