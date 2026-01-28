# Generated manually for FavoriteGallery model - v2
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


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
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='app.gallery', verbose_name='Галерея')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_galleries', to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Улюблена галерея',
                'verbose_name_plural': 'Улюблені галереї',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'gallery')},
            },
        ),
    ]
