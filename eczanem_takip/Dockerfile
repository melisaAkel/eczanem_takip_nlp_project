FROM python:3.8-slim

WORKDIR /app

# Install dependencies for OpenCV, Tesseract OCR, and other required libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmariadb-dev \
    libmariadb-dev-compat \
    tesseract-ocr \
    tesseract-ocr-tur \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy language model (en_core_web_sm)
RUN python -m spacy download en_core_web_sm

# Copy the application code
COPY . .

# Command to run the application
CMD ["python", "app.py"]
