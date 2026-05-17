from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='last_scraped_hash',
            field=models.CharField(blank=True, default='', help_text='Використовується детектором для відстеження змін', max_length=255, verbose_name='Хеш останнього сканування'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='monitoring_url',
            field=models.URLField(blank=True, default='', help_text='Посилання на сайт, Instagram або Facebook для парсингу подій', verbose_name='URL для моніторингу'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='source_type',
            field=models.CharField(blank=True, default='', help_text='Наприклад: instagram, website, facebook', max_length=50, verbose_name='Тип джерела'),
        ),
        migrations.CreateModel(
            name='Exhibition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, verbose_name='Назва виставки')),
                ('description', models.TextField(blank=True, default='', verbose_name='Опис')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата початку')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата завершення')),
                ('artists', models.JSONField(blank=True, default=list, help_text='Список художників у форматі масиву рядків', verbose_name='Художники')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна?')),
                ('source_text', models.TextField(blank=True, default='', help_text='Сирий текст, з якого AI згенерував цю виставку (для дебагу)', verbose_name='Оригінальний текст (з парсера)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exhibitions', to='app.gallery', verbose_name='Галерея')),
            ],
            options={
                'verbose_name': 'Виставка',
                'verbose_name_plural': 'Виставки',
                'db_table': 'exhibition',
                'ordering': ['-start_date'],
            },
        ),
    ]