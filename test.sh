set -e

./lint.sh

poetry run python -m unittest discover -s . -p 'test_*.py' --verbose
