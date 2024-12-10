npx pkgroll

pushd dist
cp ../package.json .
cp ../README.md .
npm publish

popd

ls -al ./dist

echo "Use the sibling project e2e-test--gpt-maa-ts to test!"
