---
hide: 
    - toc
---

# CANFAR Library Tools Schema

Schema to capture build intent, discovery metadata, and tool configuration.

### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| version | `const` | ✅ | `1` | Library manifest schema version. |
| registry | `object` | ✅ | [Registry](#registry) | Image registry. |
| maintainers | `array` | ✅ | [Maintainer](#maintainer) | Image maintainers. |
| git | `object` | ✅ | [Git](#git) | Image repository. |
| build | `object` | ✅ | [Build](#build) | Image build info. |
| metadata | `object` | ✅ | [Metadata](#metadata) | Image metadata. |
| config | `object` | ✅ | [Config](#config) | Tool configuration. |


---

# Definitions

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
| tools | `array` | ✅ | [Tool](#tool) |  | Tool definitions available to CLI steps. |  |
| cli | `object` | ✅ | object |  | CLI step name to tool id mapping. | ```{'lint': 'default-linter', 'scan': 'default-scanner'}``` |
| policy | `string` |  | `default` `strict` `expert` | `"default"` | Policy profile for tooling behavior. |  |
| conflicts | `string` |  | `warn` `strict` | `"warn"` | Conflict handling mode for tooling behavior. |  |

## Discovery

Discovery metadata mapped to OCI labels/annotations.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| title | `string` | ✅ | string |  | Human-readable title of the image. |  |
| description | `string` | ✅ | string |  | Human-readable description of the software packaged in the image. |  |
| source | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | URL to get source code for building the image |  |
| url | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | URL to find more information on the image. |  |
| documentation | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | URL to get documentation on the image |  |
| version | `string` | ✅ | string |  | Version of the packaged software. |  |
| revision | `string` | ✅ | string |  | Source control revision identifier for the packaged software. For example a git commit SHA. |  |
| created | `string` | ✅ | Format: [`date-time`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | Datetime on which the image was built. Conforming to RFC 3339 |  |
| authors | `string` | ✅ | string |  | Details of the people or organization responsible for the image |  |
| licenses | `string` | ✅ | string |  | License(s) under which contained software is distributed as an SPDX License Expression. |  |
| domain | `array` | ✅ | string |  | Scientific domains supported by this image. | ```['astronomy']```, ```['astronomy', 'scientific-computing']``` |
| kind | `array` | ✅ | `notebook` `headless` `carta` `firefly` `contributed` |  | Discovery kinds that classify this image. | ```['headless']```, ```['notebook', 'headless']``` |
| keywords | `array` |  | string |  | Keywords used to support software discovery and search. | ```astronomy```, ```analysis```, ```python``` |
| tools | `array` |  | string |  | Common tools included in the image. | ```python```, ```jupyterlab```, ```astropy``` |
| deprecated | `boolean` |  | boolean | `false` | Whether this image is deprecated and should no longer be used. |  |

## Git

Repository information for the image build source.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| repo | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) |  | Git repository. | ```https://github.com/opencadc/canfar-library``` |
| commit | `string` | ✅ | string |  | SHA commit hash to build. | ```1234567890123456789012345678901234567890``` |
| fetch | `string` |  | string | `"refs/heads/main"` | Git fetch reference. | ```refs/heads/main```, ```refs/heads/develop``` |

## Maintainer

Details about the maintainer of the image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| name | `string` | ✅ | string |  | Name of the maintainer. |
| email | `string` | ✅ | string |  | Contact email. |
| github | `string` or `null` |  | string | `null` | GitHub Username. |
| gitlab | `string` or `null` |  | string | `null` | GitLab Username. |

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

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| project | `string` | ✅ | string |  | Container registry project. | ```skaha``` |
| image | `string` | ✅ | string |  | Container image name. | ```python```, ```base``` |
| host | `string` |  | string | `"images.canfar.net"` | Container registry hostname. | ```images.canfar.net``` |

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
