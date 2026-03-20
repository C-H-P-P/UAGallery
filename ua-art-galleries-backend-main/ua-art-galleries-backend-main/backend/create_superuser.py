#!/usr/bin/env python
"""
Скрипт для створення суперкористувача Django.
Використання: python create_superuser.py
Або через Docker: docker-compose exec backend python /app/create_superuser.py
"""
import os
import sys
import django

# Налаштування Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mysite'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    username = input("Введіть ім'я користувача (або натисніть Enter для 'admin'): ").strip() or 'admin'
    
    # Перевірка чи користувач вже існує
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        if user.is_superuser:
            print(f"✓ Суперкористувач '{username}' вже існує!")
            change = input("Хочете змінити пароль? (y/n): ").strip().lower()
            if change == 'y':
                password = input("Введіть новий пароль: ").strip()
                user.set_password(password)
                user.save()
                print(f"✓ Пароль для '{username}' змінено!")
            return
        else:
            # Робимо існуючого користувача суперкористувачем
            make_super = input(f"Користувач '{username}' існує, але не є суперкористувачем. Зробити суперкористувачем? (y/n): ").strip().lower()
            if make_super == 'y':
                password = input("Введіть пароль: ").strip()
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                print(f"✓ Користувач '{username}' тепер суперкористувач!")
                return
    
    # Створення нового суперкористувача
    password = input("Введіть пароль: ").strip()
    if not password:
        print("❌ Пароль не може бути порожнім!")
        return
    
    email = input("Введіть email (опціонально): ").strip() or ''
    
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"\n✓ Суперкористувач '{username}' успішно створено!")
        print(f"\nТепер ви можете зайти в адмінку:")
        print(f"  URL: http://localhost:8000/admin/")
        print(f"  Ім'я користувача: {username}")
        print(f"  Пароль: {password}")
    except Exception as e:
        print(f"❌ Помилка при створенні суперкористувача: {e}")

if __name__ == '__main__':
    create_superuser()


