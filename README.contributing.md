# How to contribute to gpt-multi-atomic-agents

## How to publish

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
poetry publish --build
```
