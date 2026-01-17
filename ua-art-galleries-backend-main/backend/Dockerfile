FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN chmod +x /app/wait-for-db.sh

EXPOSE 8000


WORKDIR /app/mysite


CMD ["sh", "-c", "/app/wait-for-db.sh python manage.py runserver 0.0.0.0:8000"]
