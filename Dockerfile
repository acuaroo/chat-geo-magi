FROM python:3.11-slim

WORKDIR /chat-geo-magi
COPY . /chat-geo-magi

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "model.py"]
