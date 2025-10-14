# Multi-stage build for production-ready Kartavya CLI
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd --gid 1001 kartavya && \
    useradd --uid 1001 --gid kartavya --create-home --shell /bin/bash kartavya

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the application
RUN pip install --user -e .

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/kartavya/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1001 kartavya && \
    useradd --uid 1001 --gid kartavya --create-home --shell /bin/bash kartavya

# Switch to non-root user
USER kartavya
WORKDIR /home/kartavya

# Copy installed application from builder
COPY --from=builder --chown=kartavya:kartavya /root/.local /home/kartavya/.local
COPY --from=builder --chown=kartavya:kartavya /app /home/kartavya/app

# Create config directory
RUN mkdir -p /home/kartavya/.kartavya-cli

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD kartavya version || exit 1

# Default command
CMD ["kartavya", "--help"]

# Labels
LABEL maintainer="Kartavya Team <support@kartavya.dev>" \
      version="1.0.0" \
      description="Production-ready CLI for Kartavya SIEM NLP Assistant" \
      org.opencontainers.image.source="https://github.com/kartavya-team/kartavya-cli" \
      org.opencontainers.image.documentation="https://kartavya-cli.readthedocs.io" \
      org.opencontainers.image.licenses="MIT"
