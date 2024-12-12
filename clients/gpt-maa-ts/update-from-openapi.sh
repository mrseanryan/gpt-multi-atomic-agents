set -e
echo "Generating TS client from OpenAPI spec..."
kiota generate -l typescript -d ./data-openapi/gpt-maa-0.6.2.json -c PostsClient -o ./gpt_maa_client --exclude-backward-compatible

./test.sh
