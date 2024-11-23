# How to contribute to gpt-multi-atomic-agents

## How to contribute

Your contribution is welcome!

Please open a matching Issue and a Pull Request, with some explanation of the changes.

### To format and lint

```
./lint.sh
```

### To test

```
./test.sh
```

We wil try to process your PR in a reasonable time.

## How to publish [for package owner]

1. Install

```
poetry install
```

2. Create an account on pypi.org and create an API token

3. Registry your pypi.org token with poetry:

```
poetry config pypi-token.pypi <your-api-token>
```

4. Build

```
poetry build
```

5. Publish

```
poetry publish
```

Or in one command:

```
./publsh.sh
```

6. Run e2e test, to see package is consumable

```
./test.e2e.sh
```
