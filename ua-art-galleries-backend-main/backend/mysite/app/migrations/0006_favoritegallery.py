# Generated migration for FavoriteGallery model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0005_add_contentful_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='app.gallery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_galleries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'favorite_gallery',
                'unique_together': {('user', 'gallery')},
            },
        ),
    ]
