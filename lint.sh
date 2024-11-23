# so future errors halt the script.
set -e

echo Linting ...

ruff check cornsnake

echo [done]
