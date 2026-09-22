# Dockerfile - Ubuntu 22.04 + Python 3.11 (CPU)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git wget ffmpeg libglib2.0-0 libssl-dev libffi-dev \
    python3.11 python3.11-venv python3.11-distutils ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python3.11 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r /app/requirements.txt && \
    /opt/venv/bin/pip install --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || true && \
    /opt/venv/bin/pip install -e /app || true

EXPOSE 8080
CMD ["bash", "-lc", "if [ -f ./main.py ]; then python main.py || python simulate.py || bash; else bash; fi"]
