# Contributing to gpt-maa-ts

Contributions are welcome.

## Maintenance

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
./ update-from-openapi.sh
```
4. Run the test - update code as needed:

```
./test.sh
```

- tip: to test kiota in isolation, then run `./test.kiota.sh`

# References

- The REST client code is auto-generated via [kiota](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript)
