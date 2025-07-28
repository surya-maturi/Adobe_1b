FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y build-essential libjpeg-dev zlib1g-dev libpng-dev libopenjp2-7 libtiff-dev && \
    pip install --no-cache-dir pdfplumber scikit-learn numpy

# Copy your code
COPY . .

# Run
CMD ["python", "run_collections.py"]
