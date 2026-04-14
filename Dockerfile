FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src/ src/

RUN uv sync --frozen --no-dev --no-editable

ENV PATH="/app/.venv/bin:$PATH"
ENV BITOASIS_TRANSPORT=sse
ENV BITOASIS_HOST=0.0.0.0

EXPOSE 8000

ENTRYPOINT ["bitoasis-mcp"]
