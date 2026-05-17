#!/bin/bash
echo "Запуск імпорту посилань..."
cd /opt/render/project/src/ua-art-galleries-backend-main/ua-art-galleries-backend-main/backend/mysite
python manage.py import_urls galleries.csv
echo "Імпорт завершено!"
