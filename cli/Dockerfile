# Multi-stage build for Kartavya CLI
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV KARTAVYA_COLOR=true
ENV KARTAVYA_OUTPUT_FORMAT=table

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash kartavya

# Set work directory
WORKDIR /app

# Copy application from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/kartavya /usr/local/bin/kartavya
COPY --from=builder /usr/local/bin/kvya /usr/local/bin/kvya

# Copy source code
COPY src/ src/
COPY pyproject.toml ./

# Install in development mode for container
RUN pip install --no-cache-dir -e .

# Create config directory
RUN mkdir -p /home/kartavya/.config/kartavya-cli

# Change ownership
RUN chown -R kartavya:kartavya /app /home/kartavya

# Switch to non-root user
USER kartavya

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD kartavya --version || exit 1

# Default command
CMD ["kartavya", "chat", "interactive"]

# Labels
LABEL \
    org.opencontainers.image.title="Kartavya CLI" \
    org.opencontainers.image.description="Production-ready CLI for Kartavya SIEM NLP Assistant" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.vendor="Kartavya Team" \
    org.opencontainers.image.licenses="MIT"
