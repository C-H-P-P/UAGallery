# Migration to handle existing FavoriteGallery table
from django.db import migrations, models, connection
import django.db.models.deletion
from django.conf import settings


def check_table_exists(apps, schema_editor):
    """Check if table exists, if not create it"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'app_favoritegallery'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            # Table doesn't exist, create it
            cursor.execute("""
                CREATE TABLE app_favoritegallery (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    gallery_id BIGINT NOT NULL REFERENCES app_gallery(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                    UNIQUE (user_id, gallery_id)
                );
                CREATE INDEX app_favoritegallery_gallery_id ON app_favoritegallery(gallery_id);
                CREATE INDEX app_favoritegallery_user_id ON app_favoritegallery(user_id);
            """)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0005_add_contentful_fields'),
    ]

    operations = [
        migrations.RunPython(check_table_exists, reverse_code=migrations.RunPython.noop),
    ]
