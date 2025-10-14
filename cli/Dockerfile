# Multi-stage build for production-ready SYNRGY CLI
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd --gid 1001 synrgy && \
    useradd --uid 1001 --gid synrgy --create-home --shell /bin/bash synrgy

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
RUN groupadd --gid 1001 synrgy && \
    useradd --uid 1001 --gid synrgy --create-home --shell /bin/bash synrgy

# Switch to non-root user
USER synrgy
WORKDIR /home/synrgy

# Copy installed application from builder
COPY --from=builder --chown=synrgy:synrgy /root/.local /home/synrgy/.local
COPY --from=builder --chown=synrgy:synrgy /app /home/synrgy/app

# Create config directory
RUN mkdir -p /home/synrgy/.synrgy-cli

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD synrgy version || exit 1

# Default command
CMD ["synrgy", "--help"]

# Labels
LABEL maintainer="SYNRGY Team <support@synrgy.dev>" \
      version="1.0.0" \
      description="Production-ready CLI for SYNRGY SIEM NLP Assistant" \
      org.opencontainers.image.source="https://github.com/synrgy-team/synrgy-cli" \
      org.opencontainers.image.documentation="https://synrgy-cli.readthedocs.io" \
      org.opencontainers.image.licenses="MIT"
