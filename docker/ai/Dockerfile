# Production-grade AI/ML Development Image for DevForge
FROM python:3.11-bookworm

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="DevForge AI/ML development image containing PyTorch, TensorFlow, OpenCV, Whisper, and agentic frameworks."

# Install critical system tools, utility binaries, and computer vision / OCR packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    bash \
    zsh \
    zip \
    unzip \
    vim \
    nano \
    build-essential \
    ca-certificates \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install global standard dev packages
RUN pip install --no-cache-dir \
    uv \
    poetry \
    pytest \
    ruff \
    black \
    mypy \
    jupyterlab \
    uvicorn \
    gunicorn

# Install CPU PyTorch, TensorFlow, Hugging Face, OpenCV, OCR, and Whisper
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    tensorflow-cpu \
    transformers \
    datasets \
    sentencepiece \
    protobuf \
    opencv-python-headless \
    easyocr \
    pytesseract \
    openai-whisper

# Install Agentic/RAG Frameworks
RUN pip install --no-cache-dir \
    langchain \
    langchain-community \
    langchain-core \
    langchain-openai \
    langgraph \
    llama-index \
    crewai

# Configure Zsh with Oh My Zsh for a friendly developer terminal environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true

# Set up standard working directory
WORKDIR /workspace

# Create a non-privileged user and group devforge (UID 1000) for security hardening
RUN groupadd -g 1000 devforge || true && \
    useradd -u 1000 -g devforge -m -s /bin/zsh devforge || true && \
    chown -R devforge:devforge /workspace || true

# Set default user to devforge for security hardening
USER devforge

# Set up environment variables
ENV PATH="/home/devforge/.local/bin:${PATH}"

# Default command
CMD ["python"]
