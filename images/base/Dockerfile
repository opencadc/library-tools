# syntax=docker/dockerfile:1

# Build stage for pixi
# renovate: datasource=docker depName=ghcr.io/prefix-dev/pixi versioning=semver
FROM ghcr.io/prefix-dev/pixi:0.58.0@sha256:70f606d7281b16705fa39a860fc645cbbf60be89c8691b2952159b5abee9af90 AS pixi

# Build stage for uv
# renovate: datasource=docker depName=ghcr.io/astral-sh/uv versioning=semver
FROM ghcr.io/astral-sh/uv:0.9.6@sha256:4b96ee9429583983fd172c33a02ecac5242d63fb46bc27804748e38c1cc9ad0d AS uv

# CANFAR Base image
# renovate: datasource=docker depName=ubuntu versioning=ubuntu
FROM ubuntu:22.04@sha256:104ae83764a5119017b8e8d6218fa0832b09df65aae7d5a6de29a85d813da2fb AS base

LABEL org.opencontainers.image.title="CANFAR Base Image"
LABEL org.opencontainers.image.description="Base image for CANFAR Science Platform"
LABEL org.opencontainers.image.vendor="Canadian Astronomy Data Centre"
LABEL org.opencontainers.image.source="https://github.com/opencadc/canfar-library"
LABEL org.opencontainers.image.licenses="AGPL-3.0"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy binaries from build stages
COPY --from=pixi /usr/local/bin/pixi /usr/local/bin/pixi
COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

RUN set -ex; \
    apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends \
        # renovate: datasource=repology depName=ubuntu_22_04/git versioning=deb
        git=1:2.34.1-1ubuntu1.15 \
        # # renovate: datasource=repology depName=ubuntu_22_04/vim versioning=deb
        # vim=2:8.2.3995-1ubuntu2.24 \
        # # renovate: datasource=repology depName=ubuntu_22_04/emacs versioning=deb
        # emacs=1:27.1+1-3ubuntu5.2 \
        # # renovate: datasource=repology depName=ubuntu_22_04/bash-completion versioning=deb
        # bash-completion=1:2.11-5ubuntu1 \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
