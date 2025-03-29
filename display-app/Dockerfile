FROM python:3.10-slim

WORKDIR /app

# Add packages for GUI support
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libmtdev1 \
    libsdl2-dev \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY main.py discovery.py ./

# Run the app
CMD ["python", "main.py"]
