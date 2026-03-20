# Як зайти в адмінку Django

## Проблема
Адмінка не працює, тому що не створено суперкористувача.

## Рішення

### Варіант 1: Через Docker (рекомендовано)

Якщо проєкт запущений через Docker Compose:

```bash
# Створити суперкористувача інтерактивно
docker-compose exec backend python manage.py createsuperuser

# Або використати готовий скрипт
docker-compose exec backend python /app/create_superuser.py
```

### Варіант 2: Безпосередньо (якщо не використовуєте Docker)

```bash
cd artgallery/mysite
python manage.py createsuperuser
```

### Варіант 3: Швидке створення через скрипт (Docker)

```bash
docker-compose exec backend python /app/create_superuser.py
```

## Доступ до адмінки

Після створення суперкористувача:

1. Відкрийте браузер
2. Перейдіть за адресою: **http://localhost:8000/admin/**
3. Введіть ім'я користувача та пароль, які ви створили

## Що доступно в адмінці

- **Gallery** - управління галереями (створення, редагування, видалення)
- **Users** - управління користувачами (якщо додано в admin.py)

## Якщо все ще не працює

1. Перевірте, чи запущений сервер: `docker-compose ps`
2. Перевірте логи: `docker-compose logs backend`
3. Переконайтеся, що міграції виконано: `docker-compose exec backend python manage.py migrate`
4. Перевірте, чи є суперкористувач: `docker-compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([u.username for u in User.objects.filter(is_superuser=True)])"`


