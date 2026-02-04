---
hide: 
    - toc
---

# CANFAR Container Library Schema

Schema to capture ownership, build source, intent, and identity for library artifacts.

### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| registry | `object` | ✅ | [Registry](#registry) | Image registry. |
| maintainers | `array` | ✅ | [Maintainer](#maintainer) | Image maintainers. |
| git | `object` | ✅ | [Git](#git) | Image repository. |
| build | `object` | ✅ | [Build](#build) | Image build info. |
| metadata | `object` | ✅ | [Metadata](#metadata) | Image metadata. |


---

# Definitions

## Build

Configuration for building the container image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| tag | `array` | ✅ | string |  | Image tags to apply. | ```['latest']```, ```['1.0.0', 'latest']``` |
| context | `string` |  | string | `"."` | Path to the build context directory. | ```.```, ```images/python``` |
| file | `string` |  | string | `"Dockerfile"` | Name of the Dockerfile in the build context. | ```Dockerfile```, ```Dockerfile.runtime``` |
| platform | `array` |  | string | `["linux/amd64"]` | Target platforms for the build. | ```['linux/amd64']```, ```['linux/amd64', 'linux/arm64']``` |
| labels | `object` |  | object |  | Labels applied to the built image. | ```{'org.opencontainers.image.description': 'Base image for CANFAR Science Platform', 'org.opencontainers.image.title': 'CANFAR Base Image'}``` |
| annotations | `object` |  | object |  | Annotations applied to the built image. | ```{'canfar.image.runtime': 'python', 'canfar.image.type': 'runtime'}``` |
| output | `string` |  | string | `"type=docker"` | Output destination (type=docker by default). | ```type=docker```, ```type=registry```, ```type=local,dest=./out``` |
| options | `string` |  | string | `""` | Additional buildx options appended to the build command. | ```--target=runtime --push``` |

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
| name | `string` or `null` |  | string | `null` | Stylized name for the image. | ```Python```, ```astroML```, ```NumPy``` |
| description | `string` or `null` |  | Length: `string <= 255` | `null` | Short description of the image. | ```Python runtime for CANFAR Science Platform``` |
| homepage | `string` or `null` |  | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | `null` | URL to the homepage for the image. | ```https://canfar.net``` |
| guide | `string` or `null` |  | Format: [`uri`](https://json-schema.org/understanding-json-schema/reference/string#built-in-formats) | `null` | URL to the user guide for the image. | ```https://canfar.net/docs/user-guide``` |
| categories | `array` or `null` |  | string | `null` | Categories for the image. | ```development```, ```science```, ```astronomy``` |
| tools | `array` or `null` |  | string | `null` | Tools provided by the image. | ```python```, ```jupyter```, ```notebook``` |

## Registry

Details about the container registry.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| image | `string` | ✅ | string |  | Container image name. | ```python```, ```base``` |
| host | `const` |  | `https://images.canfar.net` | `"https://images.canfar.net"` | Container registry hostname. | ```https://docker.io``` |
| project | `string` |  | `library` `srcnet` `skaha` | `"library"` | Container registry namespace. | ```skaha``` |
