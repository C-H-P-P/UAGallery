import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_gallery_create():
    client = APIClient()

                     
    user = User.objects.create_user(
        username="testuser",
        password="testpass123"
    )

                
    client.force_authenticate(user=user)

    data = {
        "title": "Test Gallery",
        "description": "Test description"
    }

    response = client.post("/api/galleries/", data, format="json")

    assert response.status_code == 201
