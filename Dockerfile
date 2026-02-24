# syntax=docker/dockerfile:1

# renovate: datasource=docker depName=ghcr.io/astral-sh/uv
FROM ghcr.io/astral-sh/uv:latest@sha256:476133fa2aaddb4cbee003e3dc79a88d327a5dc7cb3179b7f02cabd8fdfbcc6e AS uv

# renovate: datasource=docker depName=python
FROM python:3.12-slim@sha256:9e01bf1ae5db7649a236da7be1e94ffbbbdd7a93f867dd0d8d5720d9e1f89fab AS base

COPY --from=uv /uv /uvx /bin/
COPY . /library
WORKDIR /library

COPY pyproject.toml README.md uv.lock ./
COPY library ./library

RUN uv pip install --system .

FROM base AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=base /usr/local /usr/local

ENTRYPOINT ["library"]
CMD ["--help"]
