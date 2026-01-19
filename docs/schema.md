---
hide: 
    - toc
---

# CANFAR Container Library Schema

Schema to capture ownership, build source, intent, and identity for library artifacts.

### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Description | Examples |
| -------- | ---- | -------- | --------------- | ----------- | -------- |
| name | `string` | ✅ | string | Image name. | ```astroml``` |
| maintainers | `array` | ✅ | [Maintainer](#maintainer) | Image maintainers. |  |
| git | `object` | ✅ | [Git](#git) | Image repository. |  |
| build | `object` | ✅ | [Build](#build) | Image build info. |  |
| metadata | `object` | ✅ | [Metadata](#metadata) | Image metadata. |  |


---

# Definitions

## Build

Configuration for building the container image.

#### Type: `object`

> ⚠️ Additional properties are not allowed.

| Property | Type | Required | Possible values | Default | Description | Examples |
| -------- | ---- | -------- | --------------- | ------- | ----------- | -------- |
| tags | `array` | ✅ | string |  | Image tags. | ```latest```, ```1.0.0``` |
| path | `string` |  | string | `"."` | Directory containing the Dockerfile. | ```.```, ```images/base``` |
| dockerfile | `string` |  | string | `"Dockerfile"` | Dockerfile. | ```Dockerfile```, ```base.Dockerfile``` |
| context | `string` |  | string | `"."` | Build context relative to path. | ```.```, ```../``` |
| builder | `string` |  | string | `"buildkit"` | Builder backend used for this entry. | ```buildkit``` |
| platforms | `array` |  | `linux/amd64` `linux/arm64` | `["linux/amd64"]` | Target platforms. | ```['linux/amd64']```, ```['linux/amd64', 'linux/arm64']``` |
| args | `object` or `null` |  | object | `null` | Build-time variables. | ```{'foo': 'bar'}``` |
| annotations | `object` or `null` |  | object | `null` | Annotations for the image. | ```{'canfar.image.runtime': 'python', 'canfar.image.type': 'runtime'}``` |
| labels | `object` or `null` |  | object | `null` | Labels for the image. | ```{'org.opencontainers.image.description': 'Base image for CANFAR Science Platform', 'org.opencontainers.image.title': 'CANFAR Base Image'}``` |
| target | `string` or `null` |  | string | `null` | Target stage to build. | ```runtime``` |
| test | `string` or `null` |  | string | `null` | Test cmd to verify the image. | ```bash -c 'echo hello world'```, ```bash -c ./test.sh``` |
| renovation | `boolean` |  | boolean | `false` | When true, canfar library will open prs to update dockerfile dependencies. | ```True```, ```False``` |

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

| Property | Type | Required | Possible values | Description |
| -------- | ---- | -------- | --------------- | ----------- |
| identifier | `string` | ✅ | string | Unique science identifier for the image. |
| project | `string` | ✅ | string | SRCnet Project name for the image. |
