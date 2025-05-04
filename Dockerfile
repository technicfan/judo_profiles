FROM python:3.13.3-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc gettext netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic \
    && django-admin compilemessages

RUN chmod +x  /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
