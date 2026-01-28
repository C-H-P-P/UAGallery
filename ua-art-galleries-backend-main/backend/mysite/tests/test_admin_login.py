import pytest
from django.contrib.auth.models import User
from django.test import Client

@pytest.mark.django_db
def test_admin_login_success():
    # створюємо тестового адміна
    User.objects.create_superuser(
        username="admin",
        password="admin123",
        email="admin@test.com"
    )

    client = Client()

    response = client.post("/admin/login/", {
        "username": "admin",
        "password": "admin123"
    })

    # якщо логін успішний — буде редірект (302)
    assert response.status_code == 302
