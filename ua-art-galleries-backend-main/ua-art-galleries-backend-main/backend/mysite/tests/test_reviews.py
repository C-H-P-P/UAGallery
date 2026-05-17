import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from app.models import Gallery, Review

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpassword123")

@pytest.fixture
def user2(db):
    return User.objects.create_user(username="testuser2", password="testpassword123")

@pytest.fixture
def gallery(db):
    return Gallery.objects.create(
        name_ua="Тестова Галерея",
        slug="test-gallery",
        status=True
    )

@pytest.mark.django_db
def test_get_reviews_public_access(api_client, gallery, user):
    Review.objects.create(user=user, gallery=gallery, rating=5, text="Чудова галерея!")
    
    response = api_client.get(f'/api/galleries/{gallery.slug}/reviews/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['rating'] == 5
    assert response.data[0]['username'] == "testuser"

@pytest.mark.django_db
def test_create_review_unauthenticated(api_client, gallery):
    response = api_client.post(f'/api/galleries/{gallery.slug}/reviews/', {
        "rating": 4,
        "text": "Спроба відгуку"
    })
    # Перевіряємо, що неавторизований юзер отримує 401 Unauthorized або 403 Forbidden
    assert response.status_code in [401, 403]

@pytest.mark.django_db
def test_create_review_authenticated(api_client, gallery, user):
    api_client.force_authenticate(user=user)
    response = api_client.post(f'/api/galleries/{gallery.slug}/reviews/', {
        "rating": 4,
        "text": "Гарно!"
    })
    
    assert response.status_code == 201
    assert response.data['rating'] == 4
    assert Review.objects.filter(gallery=gallery).count() == 1

@pytest.mark.django_db
def test_create_duplicate_review(api_client, gallery, user):
    api_client.force_authenticate(user=user)
    
    # Перший відгук - ок
    api_client.post(f'/api/galleries/{gallery.slug}/reviews/', {
        "rating": 5, "text": "Супер"
    })
    
    # Другий відгук від того ж юзера - помилка
    response = api_client.post(f'/api/galleries/{gallery.slug}/reviews/', {
        "rating": 1, "text": "Погано"
    })
    
    assert response.status_code == 400
    assert Review.objects.filter(gallery=gallery).count() == 1
