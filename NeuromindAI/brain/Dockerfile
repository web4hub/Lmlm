# Dockerfile - Reproducible environment for Brain (Ubuntu 22.04 base)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Use Python 3.11 via deadsnakes or system package
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      software-properties-common ca-certificates curl gnupg lsb-release tzdata \
      build-essential cmake git wget unzip pkg-config ffmpeg libglib2.0-0 \
      libssl-dev libffi-dev python3-dev python3-distutils python3-venv \
      python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Ensure python3 points to python3.11 (debian: python3 may be 3.10 on some images)
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.11 python3.11-venv python3.11-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    python3 --version

# Set up working dir
WORKDIR /app

# Copy project files
COPY . /app

# Create virtualenv and install Python deps
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    if [ -f "/app/requirements.txt" ]; then /opt/venv/bin/pip install -r /app/requirements.txt; fi && \
    # Install CPU PyTorch by default (remove or change for GPU)
    /opt/venv/bin/pip install --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || true && \
    /opt/venv/bin/pip install -e /app || true

ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV BRAIN_ENV=production

# Create logs dir
RUN mkdir -p /app/logs

# Expose a port if the app hosts an HTTP server (optional)
EXPOSE 8080

# Default entrypoint: run the main script if present, else start a shell
CMD ["bash", "-lc", "if [ -f ./main.py ]; then python main.py || python simulate.py || bash; else bash; fi"]

# Dockerfile - Generic reproducible environment for Brain (Ubuntu 22.04, Python 3.11)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV BRAIN_ENV=production

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      software-properties-common ca-certificates curl gnupg lsb-release tzdata \
      build-essential cmake git wget unzip pkg-config ffmpeg libglib2.0-0 \
      libssl-dev libffi-dev python3-dev python3-distutils python3-venv \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.11 python3.11-venv python3.11-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    python3 --version

WORKDIR /app

# Copy project
COPY . /app

# Create virtualenv and install python deps
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    if [ -f "/app/requirements.txt" ]; then /opt/venv/bin/pip install -r /app/requirements.txt; fi && \
    # CPU-only PyTorch install (safe default for CI); remove or change for GPU environments
    /opt/venv/bin/pip install --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || true && \
    /opt/venv/bin/pip install -e /app || true

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8080

# Default: attempt to run main.py then simulate.py, otherwise drop to shell
CMD ["bash", "-lc", "if [ -f ./main.py ]; then python main.py || python simulate.py || bash; else bash; fi"]
