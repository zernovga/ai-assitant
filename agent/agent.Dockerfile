FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ADD . /app

WORKDIR /app
RUN uv sync --locked

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]