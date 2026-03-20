#!/usr/bin/env python
"""
Скрипт для скидання пароля користувача.
Використання: docker-compose exec backend python /app/reset_user_password.py <username> <new_password>
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mysite'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Використання: python reset_user_password.py <username> <new_password>")
        print("\nАбо введіть дані вручну:")
        username = input("Ім'я користувача: ").strip()
        password = input("Новий пароль: ").strip()
    else:
        username = sys.argv[1]
        password = sys.argv[2]
    
    if not username or not password:
        print("❌ Потрібно вказати ім'я користувача та пароль!")
        sys.exit(1)
    
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"✓ Пароль для користувача '{username}' успішно змінено!")
        print(f"✓ Користувач налаштовано як суперкористувач (is_superuser=True, is_staff=True)")
        print(f"\nТепер ви можете зайти в адмінку:")
        print(f"  URL: http://localhost:8000/admin/")
        print(f"  Ім'я користувача: {username}")
        print(f"  Пароль: {password}")
    except User.DoesNotExist:
        print(f"❌ Користувач '{username}' не знайдено!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Помилка: {e}")
        sys.exit(1)


