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
| schemaVersion | `const` | ✅ | `1` | Library manifest schema version. |
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

Configuration for Library Tools execution.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| policy | `object` |  | [Policy](#policy) | Policy profile and controls. |
| tools | `object` |  | [Tools](#tools) | Tool configuration for Library Tools commands. |

## Discovery

Canonical discovery metadata mapped to OCI labels/annotations.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| title | `string` | ✅ | string | Human-readable title of the image. |
| description | `string` | ✅ | string | Human-readable description of the software packaged in the image. |
| source | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | URL to get source code for building the image |
| url | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | URL to find more information on the image. |
| documentation | `string` | ✅ | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | URL to get documentation on the image |
| version | `string` | ✅ | string | Version of the packaged software. |
| revision | `string` | ✅ | string | Source control revision identifier for the packaged software. For example a git commit SHA. |
| created | `string` | ✅ | Format: [`date-time`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | Datetime on which the image was built. Conforming to RFC 3339 |
| authors | `string` | ✅ | string | Details of the people or organization responsible for the image |
| licenses | `string` | ✅ | string | License(s) under which contained software is distributed as an SPDX License Expression. |

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

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| discovery | `object` | ✅ | [Discovery](#discovery) |  | Canonical discovery metadata. |  |
| categories | `array` or `null` |  | string | `null` | Categories for the image. | ```development```, ```science```, ```astronomy``` |
| tools | `array` or `null` |  | string | `null` | Tools provided by the image. | ```python```, ```jupyter```, ```notebook``` |

## Policy

Policy profile and enforcement configuration.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| profile | `string` |  | `baseline` `strict` `expert` | `"baseline"` | Policy profile for tooling behavior. |
| conflicts | `string` |  | `warn` `strict` | `"warn"` | How to handle discovered conflicts. |

## Registry

Details about the container registry.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| image | `string` | ✅ | string |  | Container image name. | ```python```, ```base``` |
| host | `string` |  | string | `"images.canfar.net"` | Container registry hostname. | ```images.canfar.net``` |
| project | `string` |  | `library` `srcnet` `skaha` | `"library"` | Container registry namespace. | ```skaha``` |

## Runner

Docker runner configuration (P0).

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| image | `string` | ✅ | string |  | Container image to run. |
| command | `array` | ✅ | string |  | Command to execute in the container. |
| kind | `const` |  | `docker` | `"docker"` | Runner type. |
| env | `object` or `null` |  | object | `null` | Environment variables for the container. |

## Tool

Configuration for tooling.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description |
| -------- | ---- | -------- | --------------- | ------- | ----------- |
| parser | `string` | ✅ | `hadolint` `trivy` `renovate` `curate` `provenance` `push` |  | Parser to use for the tool output. |
| output | `string` | ✅ | string |  | Path to write the tool output artifact. |
| config | `string` or `null` |  | string | `null` | Path to the tool configuration file. |
| runner | `object` or `null` |  | [Runner](#runner) | `null` | Runner configuration for tool execution. |

## Tools

Fixed tool configuration set for Library Tools commands.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| lint | `object` |  | [Tool](#tool) | Lint command configuration. |
| scan | `object` |  | [Tool](#tool) | Scan command configuration. |
| refurbish | `object` |  | [Tool](#tool) | Refurbish command configuration. |
| curate | `object` |  | [Tool](#tool) | Curate command configuration. |
| provenance | `object` |  | [Tool](#tool) | Provenance command configuration. |
| push | `object` |  | [Tool](#tool) | Push command configuration. |
