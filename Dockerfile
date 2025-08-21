FROM python:3.13-slim

# Prevent Python from writing .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PORT=8000

ENV PATH="/root/.cargo/bin/:$PATH"

# System dependencies: ffmpeg for audio handling, fonts for Pillow font loading
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
       ffmpeg \
       fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install uv 
# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# Copy dependency manifests first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Copy the application code
COPY . .

# Install Python dependencies into a local virtualenv managed by uv
RUN uv sync --frozen --no-dev



# Expose default port; Railway will set PORT env var at runtime
EXPOSE 8000

# Start FastAPI using uv as in the Makefile, binding to Railway's PORT
CMD ["sh", "-lc", "uv run uvicorn src.server:app --host 0.0.0.0 --port ${PORT}"]


