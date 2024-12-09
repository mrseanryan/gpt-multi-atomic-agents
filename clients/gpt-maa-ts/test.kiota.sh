set -e

echo "Generating TS client from OpenAPI spec..."
kiota generate -l typescript -d ./data-openapi/jsonplaceholder.typicode.com.yaml -c PostsClient -o ./test_client --exclude-backward-compatible

echo "Executing the client..."
npx tsx ./src/test_kiota_client.ts
