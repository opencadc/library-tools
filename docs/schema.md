---
hide: 
    - toc
---

# CANFAR Library Tools Schema

Schema to capture build intent, discovery metadata, and tool configuration.

### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| registry | `object` | ✅ | [Registry](#registry) |  | Image registry. |
| build | `object` | ✅ | [Build](#build) |  | Image build info. |
| metadata | `object` | ✅ | [Metadata](#metadata) |  | Image metadata. |
| config | `object` | ✅ | [Config](#config) |  | Tool configuration. |
| version | `const` |  | `1` | `1` | Library manifest schema version. |


---

# Definitions

## Author

Details about an author of the image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| name | `string` | ✅ | string |  | Name of the author. | ```John Doe``` |
| email | `string` | ✅ | string |  | Contact email address for the author. | ```john.doe@example.com``` |
| github | `string` or `null` |  | string | `null` | GitHub Username. | ```johndoe``` |
| gitlab | `string` or `null` |  | string | `null` | GitLab Username. | ```johndoe``` |
| orcid | `string` or `null` |  | string | `null` | Open Researcher and Contributor ID. | ```0000-0002-1825-0097``` |
| affiliation | `string` or `null` |  | string | `null` | Affiliation of the author. | ```Oxford University``` |
| role | `string` |  | `maintainer` `contributor` | `"maintainer"` | Role of the author. | ```Maintainer```, ```Contributor``` |

## Build

Configuration for building the container image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| tags | `array` | ✅ | string |  | Image tags to apply. | ```['latest']```, ```['1.0.0', 'latest']``` |
| context | `string` |  | string | `"."` | Path to the build context directory. | ```.```, ```images/python``` |
| file | `string` |  | string | `"Dockerfile"` | Name of the Dockerfile in the build context. | ```Dockerfile```, ```Dockerfile.runtime``` |
| platforms | `array` |  | string | `["linux/amd64"]` | Target platforms for the build. | ```['linux/amd64']```, ```['linux/amd64', 'linux/arm64']``` |
| output | `string` |  | string | `"type=docker"` | Output destination (type=docker by default). | ```type=docker```, ```type=registry```, ```type=local,dest=./out``` |
| options | `string` |  | string | `""` | Additional buildx options appended to the build command. | ```--target=runtime --push``` |

## Config

Configuration for Library Tools execution and CLI wiring.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| policy | `string` |  | `default` `strict` `expert` | `"default"` | Policy profile for tooling behavior. |  |
| conflicts | `string` |  | `warn` `strict` | `"warn"` | Conflict handling mode for tooling behavior. |  |
| tools | `array` |  | [Tool](#tool) |  | Tool definitions available to CLI steps. |  |
| cli | `object` |  | object |  | CLI step name to tool id mapping. | ```{'lint': 'default-linter', 'scan': 'default-scanner'}``` |

## Discovery

Discovery metadata mapped to OCI labels/annotations.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| title | `string` | ✅ | string |  | Human-readable title of the image. | ```Baseband Analysis``` |
| description | `string` | ✅ | Length: `1 <= string <= 255` |  | Human-readable description of the software packaged in the image. | ```Baseband analysis tools for radio astronomy.``` |
| source | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | URL to get source code for building the image. | ```https://github.com/example/repo``` |
| version | `string` | ✅ | string |  | Version of the packaged software. | ```1.0.0``` |
| revision | `string` | ✅ | string |  | Source control revision identifier for the packaged software. | ```1234567890123456789012345678901234567890``` |
| created | `string` | ✅ | Format: [`date-time`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | Datetime on which the image was built. Conforming to RFC 3339. | ```2026-02-05T12:00:00Z``` |
| authors | `array` | ✅ | [Author](#author) |  | Details of the people or organization responsible for the image | ```{'email': 'john.doe@example.com', 'name': 'John Doe'}``` |
| licenses | `string` | ✅ | string |  | License(s) under which contained software is distributed as an SPDX License Expression. | ```AGPL-3.0```, ```AGPL-3.0-only```, `````` |
| keywords | `array` | ✅ | string |  | Keywords used to support software discovery and search. | ```astronomy```, ```analysis```, ```python``` |
| kind | `array` | ✅ | `notebook` `headless` `carta` `firefly` `contributed` `desktop` |  | Discovery kinds that classify this image. | ```['headless']```, ```['notebook', 'headless']``` |
| url | `string` or `null` |  | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | `null` | URL to find more information on the image. | ```https://example.com/baseband-analysis``` |
| documentation | `string` or `null` |  | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | `null` | URL to get documentation on the image. | ```https://example.com/baseband-analysis/docs``` |
| domain | `array` |  | string | `["astronomy"]` | Scientific domains supported by this image. | ```['astronomy']```, ```['astronomy', 'scientific-computing']``` |
| tools | `array` |  | string |  | Common tools included in the image. | ```python```, ```jupyterlab```, ```astropy``` |
| deprecated | `boolean` |  | boolean | `false` | Whether this image is deprecated and should no longer be used. | ```False```, ```True``` |

## Metadata

Metadata for the image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| discovery | `object` | ✅ | [Discovery](#discovery) | Canonical discovery metadata. |

## Registry

Details about the container registry.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description | Examples |
| -------- | ---- | -------- | --------------- | ----------- | -------- |
| host | `string` | ✅ | string | Container registry hostname. | ```images.canfar.net```, ```docker.io``` |
| project | `string` | ✅ | string | Container registry project/namespace. | ```skaha```, ```chimefrb``` |
| image | `string` | ✅ | string | Container image name. | ```python```, ```baseband-analysis``` |

## Tool

Definition of a Library Tool.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| id | `string` | ✅ | [`^[a-zA-Z0-9][a-zA-Z0-9._-]*$`](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9%5D%5Ba-zA-Z0-9._-%5D%2A%24) |  | Unique tool identifier. | ```default-scanner```, ```srcnet-scanner``` |
| parser | `string` | ✅ | `hadolint` `trivy` `renovate` `curate` `provenance` `push` |  | Built-in parser used to consume the tool JSON outputs. | ```trivy```, ```hadolint``` |
| image | `string` | ✅ | string |  | Container image to run the tool in. | ```docker.io/aquasec/trivy:latest``` |
| command | `array` | ✅ | string |  | Tokenized command argv executed in the tool container. Supported tokens: {{inputs.<key>}} and {{image.reference}}. | ```['trivy', 'image', '--config', '{{inputs.trivy}}', '--format', 'json', '--output', '/outputs/report.json', '{{image.reference}}']``` |
| env | `object` |  | object |  | Environment variables passed to the tool container. |  |
| inputs | `object` |  | [ToolInputs](#toolinputs) |  | Tool inputs mounted into the tool container. |  |
| socket | `boolean` |  | boolean | `false` | Whether /var/run/docker.sock is mounted into the tool container. |  |
| outputs | `const` |  | `/outputs/` | `"/outputs/"` | Fixed container directory where tools must write outputs. | ```/outputs/``` |

## ToolInputs

Named tool inputs resolved by CLI into deterministic mounts.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| source | `const` or `string` |  | Format: [`file-path`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) and/or `default` | `"default"` | Input source for the tool. 'default' maps to built-in config shipped with the library; otherwise provide a local file path. | ```default```, ```./ci/.trivy.yaml``` |
| destination | `string` |  | string | `"/config.yaml"` | Absolute path in the tool container where the input is mounted. | ```/config.yaml```, ```/workspace/config/trivy.yaml``` |
