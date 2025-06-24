FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/app

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

FROM python:3.13-slim-bookworm

ENV PATH=/app/bin:$PATH

RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

COPY --from=builder --chown=app:app /app /app

COPY . /app/

USER app
WORKDIR /app

CMD ["python3", "/app/main.py"]