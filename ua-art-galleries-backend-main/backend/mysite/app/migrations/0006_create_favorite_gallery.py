# Migration to create favorite_gallery table with correct name
from django.db import migrations, connection
from django.conf import settings


def create_favorite_gallery_table(apps, schema_editor):
    """Drop old table if exists and create new one with correct name"""
    with connection.cursor() as cursor:
        # Drop old table if exists
        cursor.execute("DROP TABLE IF EXISTS app_favoritegallery CASCADE;")
        
        # Create new table with correct name
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorite_gallery (
                id BIGSERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                gallery_id BIGINT NOT NULL REFERENCES public_gallery(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                UNIQUE (user_id, gallery_id)
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS favorite_gallery_gallery_id ON favorite_gallery(gallery_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS favorite_gallery_user_id ON favorite_gallery(user_id);")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0005_add_contentful_fields'),
    ]

    operations = [
        migrations.RunPython(create_favorite_gallery_table, reverse_code=migrations.RunPython.noop),
    ]
