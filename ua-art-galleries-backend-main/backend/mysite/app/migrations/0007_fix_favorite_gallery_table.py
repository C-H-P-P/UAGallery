# Fix for FavoriteGallery table - ensures table exists
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_favoritegallery'),
    ]

    operations = [
        migrations.RunSQL(
            # Create table if it doesn't exist
            sql="""
            CREATE TABLE IF NOT EXISTS favorite_gallery (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                gallery_id BIGINT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                CONSTRAINT favorite_gallery_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
                CONSTRAINT favorite_gallery_gallery_id_fkey 
                    FOREIGN KEY (gallery_id) REFERENCES public_gallery(id) ON DELETE CASCADE,
                CONSTRAINT favorite_gallery_user_gallery_unique 
                    UNIQUE (user_id, gallery_id)
            );
            
            CREATE INDEX IF NOT EXISTS favorite_gallery_user_id_idx ON favorite_gallery(user_id);
            CREATE INDEX IF NOT EXISTS favorite_gallery_gallery_id_idx ON favorite_gallery(gallery_id);
            """,
            # Reverse - drop table
            reverse_sql="DROP TABLE IF EXISTS favorite_gallery CASCADE;"
        ),
    ]
