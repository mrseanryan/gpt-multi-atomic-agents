# gpt-maa-ts README (gpt-multi-atomic-agents - TypeScript Client)

A TypeScript client for submitting AgentDefinitions and user prompts to a gpt-multi-atomic-agents REST API, to generate supported mutations (function calls).

This client provides a mini framework for defining the Agents and handling the response.

This provides a clean approach to LLM based Agent calling, so the client can focus on the 'domain' or business logic:

- submit data in the form of Function Calls
- process the generated mutations, updating the application data

For an example with simple Agents, see [TypeScript Example Agents](https://github.com/mrseanryan/gpt-multi-atomic-agents/tree/master/clients/gpt-maa-ts/src/test_gpt_maa_client.ts).

# Setup

Install the depdencencies:

- [Node](https://nodejs.org/en/download/package-manager) v20.18+
- [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/install?tabs=bash)

note: You need to add the kioto install location to your system path environment variable

```
./install.sh
```

# Usage

# Test

```
./test.sh
```

## Mainenance

To update the client, if the REST API has changed:

1. Copy the OpenAPI JSON from the Swagger site and paste into `gpt-maa-0.6.0.json`
2. Edit the JSON to be OpenAPI Version 3.0.0 (not 3.1.1):
    - see the existing files for differences
    - set `openapi` version to `"3.0.0"`
    - change `examples` -> `example`
    - [add `servers` section]
    - replace `"type": "null"` with `"nullable": true`

3. Run kyoto to generate the TypeScript client
```
./build.sh
```
4. Run the test - update code as needed:

```
./test.sh
```

- tip: to test kiota in isolation, then run `./test.kiota.sh`

# References

- The REST client code is auto-generated via [kiota](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript)
