set -e

./test.sh

poetry publish --build

echo To install the package:
echo python -m pip install gpt-multi-atomic-agents
