set -e

npm add gpt-maa-ts@latest 
ls -al node_modules/gpt-maa-ts   

echo "Executing the e2e test client..."
npx tsx ./src/index.ts
