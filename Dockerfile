FROM python:3.9-slim

ENV VENV_PATH="/venv"
ENV PATH="$VENV_PATH/bin:$PATH"
ENV PYTHONPATH="/app"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install ONLY dependencies (no root package)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root --no-interaction --no-ansi

# NOW copy the rest of your modified code (including README if you want)
COPY . .

EXPOSE 8081

# We stay with uvicorn, but we ensure the working directory is clear
CMD ["python", "-m", "uvicorn", "bhagavad_gita_api.main:app", "--host", "0.0.0.0", "--port", "8081"]