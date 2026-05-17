from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0010_gallery_contentful_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Оцінка')),
                ('text', models.TextField(help_text='Коментар користувача про галерею', verbose_name='Текст відгуку')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Час створення')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Час оновлення')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='app.gallery', verbose_name='Галерея')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Відгук',
                'verbose_name_plural': 'Відгуки',
                'db_table': 'gallery_review',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'gallery')},
            },
        ),
    ]