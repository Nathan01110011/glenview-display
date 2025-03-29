FROM python:3.9-slim

# Install required system libs for Kivy headless mode (no UI)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgles2-mesa \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    libmtdev1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "main.py"]
