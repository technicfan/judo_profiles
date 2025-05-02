FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic

RUN chmod +x  /app/start.sh

CMD ["/app/start.sh"]
