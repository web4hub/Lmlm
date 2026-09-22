#!/usr/bin/env bash
set -euo pipefail

PYTHON=python3
VENV_DIR=.venv

echo "Creating virtualenv in ${VENV_DIR}..."
${PYTHON} -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

pip install --upgrade pip setuptools wheel
echo "Installing pip requirements..."
pip install -r requirements.txt || {
  echo "pip install failed; you may need system packages. See apt-get suggestions below."
  exit 1
}

echo "Installing CPU PyTorch (if not already installed). Adjust for CUDA/Jetson as needed..."
pip install --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || true

echo
echo "Done. Activate with: source ${VENV_DIR}/bin/activate"
echo
echo "If you are on Ubuntu, you may need to install system packages:"
echo "  sudo apt-get update && sudo apt-get install -y build-essential cmake libssl-dev libffi-dev python3-dev ffmpeg libglib2.0-0"
echo
echo "If you use ROS2, install rclpy and other ROS2 packages via apt on an Ubuntu/ROS image."
echo "If you are on Jetson, follow NVIDIA's instructions to install JetPack and a JetPack-compatible PyTorch wheel."
