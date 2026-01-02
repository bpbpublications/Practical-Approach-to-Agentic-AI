FROM python:3.11-slim-bookworm

# Set recommended environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

# Install system dependencies and Poetry
RUN apt-get update \
    && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /app

# Copy poetry files first for layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (set up application dependencies in container)
RUN poetry install --no-root --no-ansi

# Copy app source code
COPY . .

# Expose Chainlit port
EXPOSE 8000

# Run Chainlit with host and port suitable for Docker
CMD ["poetry", "run", "chainlit", "run", "src/Chapter11/af_chainlit_simple_weather_agent_no_trace.py", "--host", "0.0.0.0", "--port", "8000"]