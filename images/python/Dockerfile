# syntax=docker/dockerfile:1

# renovate: datasource=docker depName=ghcr.io/prefix-dev/pixi versioning=semver
FROM ghcr.io/prefix-dev/pixi:0.58.0@sha256:70f606d7281b16705fa39a860fc645cbbf60be89c8691b2952159b5abee9af90 AS pixi

# renovate: datasource=docker depName=ghcr.io/astral-sh/uv versioning=semver
FROM ghcr.io/astral-sh/uv:0.9.1@sha256:3b368e735c0227077902233a73c5ba17a3c2097ecdd83049cbaf2aa83adc8a20 AS uv

FROM python:3.10-slim AS base

LABEL org.opencontainers.image.title="CANFAR Python Runtime" \
      org.opencontainers.image.description="Python runtime for CANFAR Science Platform" \
      org.opencontainers.image.vendor="Canadian Astronomy Data Centre" \
      org.opencontainers.image.source="https://github.com/opencadc/canfar-library" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy binaries from build stages
COPY --from=pixi /usr/local/bin/pixi /usr/local/bin/pixi
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

ENV UV_PYTHON_INSTALL_DIR=/usr/local/share/uv/python \
    UV_PYTHON_BIN_DIR=/usr/local/bin \
    UV_TOOL_DIR=/usr/local/share/uv/tools \
    UV_TOOL_BIN_DIR=/usr/local/bin

RUN uv tool install --no-cache canfar==1.2.0
