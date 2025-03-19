FROM python:3.13-slim AS builder

WORKDIR /app

# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x  /app/start.sh

CMD ["/app/start.sh"]
