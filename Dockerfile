FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR for Multi-Modal analysis
# (rus/kaz/ara/eng pipelines; eng ships with tesseract-ocr, listed explicitly for clarity)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    tesseract-ocr-kaz \
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

# Writable runtime dirs (SQLite DB, B2B keys, feedback) + non-root execution.
# Runtime state lives under /app/data; on a platform with persistent storage,
# mount a volume/disk here to survive deploy+restart cycles.
RUN mkdir -p /app/data && chmod -R a+w /app/data && \
    useradd -m -u 1000 appuser && chown -R appuser:appuser /app
VOLUME ["/app/data"]
USER appuser

ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:${PORT}/api/v1/health', timeout=5).status == 200 else 1)"

CMD ["python", "start_all.py"]
