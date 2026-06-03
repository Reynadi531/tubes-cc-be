FROM python:3.12-alpine

# Install build dependencies required for native extensions
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into a virtual environment
RUN uv sync --no-dev --frozen

# Copy application source
COPY . .

# Add the virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

ENV PORT=8000

EXPOSE ${PORT}

CMD uvicorn api:app --host 0.0.0.0 --port ${PORT}
