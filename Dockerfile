# 1. Base Image
FROM python:3.10-slim-bullseye

# 2. Environment Variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Kolkata"

# 3. Set Working Directory
WORKDIR /app

# 4. Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git wget pv jq python3-dev \
    mediainfo gcc libsm6 libxext6 \
    libfontconfig1 libxrender1 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# 6. Copy Bot files
COPY . .

# 7. Run the bot
CMD ["python3", "-m", "VideoEncoder"]
