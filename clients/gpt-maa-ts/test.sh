echo "Generating TS client from OpenAPI spec..."
kiota generate -l typescript -d ./data-openapi/jsonplaceholder.typicode.com.yaml -c PostsClient -o ./client --exclude-backward-compatible

echo "Executing the client..."
npx tsx ./src/test_client.ts
