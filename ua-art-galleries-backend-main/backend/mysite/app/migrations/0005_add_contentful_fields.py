# Generated manually for adding Contentful fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_gallery_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Slug'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='status',
            field=models.BooleanField(default=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='cover_image',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='Cover Image URL'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='short_description_ua',
            field=models.TextField(blank=True, null=True, verbose_name='Короткий опис (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='short_description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Short Description (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='full_description_ua',
            field=models.TextField(blank=True, null=True, verbose_name='Повний опис (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='full_description_en',
            field=models.TextField(blank=True, null=True, verbose_name='Full Description (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='specialization_ua',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Спеціалізація (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='specialization_en',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Specialization (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='city_ua',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Місто (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='city_en',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='City (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='address_ua',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Адреса (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='address_en',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Address (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='founders_ua',
            field=models.TextField(blank=True, null=True, verbose_name='Засновники (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='founders_en',
            field=models.TextField(blank=True, null=True, verbose_name='Founders (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='curators_ua',
            field=models.TextField(blank=True, null=True, verbose_name='Куратори (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='curators_en',
            field=models.TextField(blank=True, null=True, verbose_name='Curators (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='artists_ua',
            field=models.TextField(blank=True, null=True, verbose_name='Художники (UA)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='artists_en',
            field=models.TextField(blank=True, null=True, verbose_name='Artists (EN)'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='email',
            field=models.EmailField(blank=True, max_length=200, null=True, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='website',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='Веб-сайт'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='social_links',
            field=models.JSONField(blank=True, null=True, verbose_name='Соціальні мережі'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='founding_year',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Рік заснування'),
        ),
    ]
