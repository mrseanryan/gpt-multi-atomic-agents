set -e
poetry run python -m unittest discover -s . -p test_sim_life_via*.py --verbose
