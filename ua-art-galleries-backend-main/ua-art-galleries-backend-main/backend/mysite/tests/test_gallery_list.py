import pytest
from django.test import Client
from app.models import Gallery

@pytest.mark.django_db
def test_gallery_list_returns_200():
    client = Client()

    response = client.get("/api/galleries/")

    assert response.status_code == 200
