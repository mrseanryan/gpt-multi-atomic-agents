# so future errors halt the script.
set -e

echo Linting ...

ruff check .

echo [done]
