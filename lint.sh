# so future errors halt the script.
set -e

echo Formatting ...
ruff format

echo Linting ...
ruff check .

poetry run python -m mypy --install-types --non-interactive gpt_multi_atomic_agents

echo [done]
