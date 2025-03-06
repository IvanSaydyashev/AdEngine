FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /env
ENV PATH="/env/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8080"]
