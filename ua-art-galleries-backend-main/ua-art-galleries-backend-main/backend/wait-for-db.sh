#!/bin/sh
echo "Чекаємо, поки PostgreSQL запуститься..."
until nc -z db 5432; do
  echo "PostgreSQL ще не готовий... (чекаємо 1 сек)"
  sleep 1
done
echo "PostgreSQL запущений! Запускаємо Django..."
exec "$@"