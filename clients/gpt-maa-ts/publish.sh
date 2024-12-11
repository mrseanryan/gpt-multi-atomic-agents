set -e

rm -rf dist
npx pkgroll

pushd dist

mkdir dist
mv index.* dist
cp ../package.json .
cp ../README.md .

npm publish .

popd

find ./dist

echo "Use the sibling project e2e-test--gpt-maa-ts to test!"
