set -e

pushd ./tests/e2e

echo "Installing gpt-multi-atomic-agents via pip, to test that the package can be consumed OK"

python -m pip install --upgrade gpt-multi-atomic-agents --quiet

python -m e2e_test_install
