FROM ubuntu:22.04

# Avoid user interaction during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required by Blender's C++ core
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libgl1 \
    libxi6 \
    libxrender1 \
    libxkbcommon0 \
    libsm6 \
    libxext6 \
    libvulkan1 \
    libxxf86vm1 \
    libxcursor1 \
    libxinerama1 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# Define Blender version parameters
ENV BLENDER_MAJOR=5.1
ENV BLENDER_VERSION=5.1.1
ENV BLENDER_URL=https://download.blender.org/release/Blender${BLENDER_MAJOR}/blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Download and extract Blender directly to /usr/local/bin
RUN wget ${BLENDER_URL} \
    && tar -xvf blender-${BLENDER_VERSION}-linux-x64.tar.xz --strip-components=1 -C /usr/local/bin \
    && rm blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Ensure pip is installed within Blender's embedded Python (3.13 for Blender 5.1)
RUN /usr/local/bin/${BLENDER_MAJOR}/python/bin/python3.13 -m ensurepip
RUN /usr/local/bin/${BLENDER_MAJOR}/python/bin/python3.13 -m pip install --upgrade pip

# Install the machine learning and math stack into Blender's Python
# We also install 'fake-bpy-module-latest' purely for VS Code autocomplete
RUN /usr/local/bin/${BLENDER_MAJOR}/python/bin/python3.13 -m pip install \
    numpy \
    torch \
    albumentations \
    fake-bpy-module-latest

# Set the working directory
WORKDIR /workspace

# Keep the container alive for VS Code to attach to
CMD ["sleep", "infinity"]
