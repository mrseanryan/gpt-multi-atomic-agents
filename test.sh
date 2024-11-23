set -e

./lint.sh

poetry run python -m unittest discover -s . -p 'test_unit*.py' --verbose

poetry run python -m unittest discover -s . -p 'test_*.py' --verbose
