# Contributing to gpt-maa-ts

Contributions are welcome.

## Setup (for contributing)

Install the depdencencies:

- [Node](https://nodejs.org/en/download/package-manager) v20.18+
- (for contributing) [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/install?tabs=bash)

> **_NOTE:_** You need to add the kioto install location to your system path environment variable

```
./install.sh
```

## Debugging

Tips:

- open Visual Code at this 'client' project, so then you can debug
- open the relevant 'test entry' file
  - for REPL = `test_gpt_maa_client_repl.ts`
- press F5

## Maintenance

To update the client, if the REST API has changed:

1. Copy the OpenAPI JSON from the Swagger site and paste into `gpt-maa-current.json`

- Optionally, also paste it into a versioned file like `gpt-maa-0.7.0.openapi-3.1.1.json`

2. Edit the JSON to be OpenAPI Version 3.0.0 (not 3.1.1):

   - see the existing files for differences
   - set `openapi` version to `"3.0.0"`
   - change `examples` -> `example`
   - [add `servers` section]
   - replace `"type": "null"` with `"nullable": true`

3. Run kyoto to generate the TypeScript client

```
./update-from-openapi.sh
```

4. Run the test - update code as needed:

```
./test.sh
```

- tip: to test kiota in isolation, then run `./test.kiota.sh`

# References

- The REST client code is auto-generated via [kiota](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript)
