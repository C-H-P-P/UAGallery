#!/usr/bin/env python
"""
Скрипт для тестування входу в адмінку та виправлення проблем.
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mysite'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.test import Client

User = get_user_model()

def test_login(username, password):
    """Тестує вхід користувача"""
    print(f"\n🔍 Тестування входу для користувача: {username}")
    
    # Перевірка чи користувач існує
    try:
        user = User.objects.get(username=username)
        print(f"✓ Користувач знайдено: {username}")
        print(f"  - is_superuser: {user.is_superuser}")
        print(f"  - is_staff: {user.is_staff}")
        print(f"  - is_active: {user.is_active}")
    except User.DoesNotExist:
        print(f"❌ Користувач '{username}' не знайдено!")
        return False
    
    # Тестування аутентифікації
    user_auth = authenticate(username=username, password=password)
    if user_auth:
        print(f"✓ Аутентифікація успішна!")
        print(f"  - Можна зайти в адмінку: {user_auth.is_superuser and user_auth.is_staff}")
        return True
    else:
        print(f"❌ Аутентифікація не вдалася - неправильний пароль!")
        return False

def fix_user(username):
    """Виправляє налаштування користувача"""
    try:
        user = User.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"✓ Користувач '{username}' виправлено (is_superuser=True, is_staff=True, is_active=True)")
        return True
    except User.DoesNotExist:
        print(f"❌ Користувач '{username}' не знайдено!")
        return False

def list_superusers():
    """Показує всіх суперкористувачів"""
    users = User.objects.filter(is_superuser=True)
    print("\n📋 Список суперкористувачів:")
    for user in users:
        print(f"  - {user.username} (staff={user.is_staff}, active={user.is_active})")

if __name__ == '__main__':
    list_superusers()
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else None
        
        if password:
            test_login(username, password)
        else:
            print(f"\nВикористання: python test_admin_login.py <username> <password>")
            print(f"Або для виправлення: python test_admin_login.py --fix <username>")
    else:
        print("\nВикористання:")
        print("  python test_admin_login.py <username> <password>  - тестування входу")
        print("  python test_admin_login.py --fix <username>       - виправлення користувача")
        print("\nАбо введіть дані вручну:")
        username = input("Ім'я користувача: ").strip()
        password = input("Пароль: ").strip()
        if username and password:
            test_login(username, password)


