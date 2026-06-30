# Dockerfile for RunPod - WARABA-DIRECTOR + JoyAI-Echo
# Optimized for H100 / A100 / L40S GPUs

FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# Install PyTorch with CUDA 12.8 support
RUN pip install torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install common dependencies
RUN pip install \
    fastapi \
    uvicorn[standard] \
    pydantic \
    python-multipart \
    huggingface_hub \
    accelerate \
    safetensors \
    einops \
    diffusers \
    transformers \
    opencv-python-headless \
    pillow \
    numpy \
    scipy \
    tqdm

# Clone JoyAI-Echo repository
RUN git clone https://github.com/jd-opensource/JoyAI-Echo.git /app/JoyAI-Echo

# Set working directory
WORKDIR /app

# Copy your custom code (FastAPI, prompt assembler, etc.)
COPY . /app/

# Create directories for model weights and outputs
RUN mkdir -p /app/models /app/outputs /app/prompts

# Expose FastAPI port
EXPOSE 8000

# Default command (can be overridden in RunPod template)
CMD ["uvicorn", "runpod_fastapi_skeleton:app", "--host", "0.0.0.0", "--port", "8000"]