# Виправлення проблеми з входом в адмінку

## Проблема
Створено суперкористувача, але не вдається зайти в адмінку.

## Можливі причини та рішення

### 1. Неправильний пароль
Найчастіша причина - неправильно введений пароль при створенні або вході.

**Рішення:** Скиньте пароль:
```powershell
docker-compose exec backend python /app/reset_user_password.py <username> <new_password>
```

Наприклад:
```powershell
docker-compose exec backend python /app/reset_user_password.py dima mynewpassword123
```

### 2. Проблеми з кешем браузера
Браузер може зберігати старі сесії або cookies.

**Рішення:**
- Очистіть cookies для `localhost:8000`
- Або використайте режим інкогніто/приватного перегляду
- Або відкрийте в іншому браузері

### 3. Перевірка користувача
Переконайтеся, що користувач має правильні налаштування:

```powershell
docker-compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='dima'); print(f'is_superuser: {u.is_superuser}, is_staff: {u.is_staff}, is_active: {u.is_active}')"
```

### 4. Тестування входу програмно
Перевірте, чи працює аутентифікація:

```powershell
docker-compose exec backend python /app/test_admin_login.py dima yourpassword
```

## Швидке виправлення

1. **Скиньте пароль для існуючого користувача:**
   ```powershell
   docker-compose exec backend python /app/reset_user_password.py dima newpassword123
   ```

2. **Або створіть нового користувача з відомим паролем:**
   ```powershell
   docker-compose exec backend python /app/create_superuser.py
   ```

3. **Очистіть cookies браузера** або використайте **режим інкогніто**

4. **Спробуйте зайти:** http://localhost:8000/admin/

## Якщо все ще не працює

1. Перевірте логи сервера:
   ```powershell
   docker-compose logs backend
   ```

2. Перевірте, чи сервер запущений:
   ```powershell
   docker-compose ps
   ```

3. Перезапустіть контейнери:
   ```powershell
   docker-compose restart backend
   ```

4. Перевірте, чи адмінка доступна (має показати форму входу):
   - Відкрийте: http://localhost:8000/admin/
   - Має з'явитися форма входу Django Admin

## Список існуючих суперкористувачів

Зараз у вас є такі суперкористувачі:
- AAA
- dima  
- d

Використайте один з них або створіть нового з відомим паролем.


