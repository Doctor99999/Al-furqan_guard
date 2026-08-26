FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR for Multi-Modal analysis
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-ara \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set up isolated virtual environment (best practice, suppresses root warning)
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PIP_ROOT_USER_ACTION=ignore

COPY requirements.txt requirements.lock .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -c requirements.lock

COPY . .

# Writable runtime dirs (SQLite DB, feedback, analytics) + non-root execution
RUN mkdir -p /app/data && chmod -R a+w /app/data && \
    useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["python", "start_all.py"]
