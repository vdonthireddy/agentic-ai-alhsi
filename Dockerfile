FROM python:3.12-slim

# Install system dependencies (git is required for the Agent Loop commit/revert engine)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure git credentials for autonomous loop commits
RUN git config --global user.name "Autonomous Loop Agent" \
    && git config --global user.email "agent@autoresearch.local"

WORKDIR /app

# Copy project definition and source code
COPY pyproject.toml README.md ./
COPY alhsi/ ./alhsi/
COPY tests/ ./tests/

# Install python dependencies and the alhsi package
RUN pip install --no-cache-dir -e . && pip install --no-cache-dir pytest httpx httpx2

# Create directory for sandbox experiments
RUN mkdir -p /root/.alhsi

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=3 \
  CMD curl -f http://localhost:8000/api/state || exit 1

CMD ["python3", "-m", "alhsi", "serve", "--host", "0.0.0.0", "--port", "8000"]
