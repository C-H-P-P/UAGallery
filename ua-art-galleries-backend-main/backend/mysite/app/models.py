from django.db import models

class Gallery(models.Model):
    # Назви залишаємо обов'язковими
    name_ua = models.CharField(max_length=200, verbose_name="Назва (UA)")
    name_en = models.CharField(max_length=200, verbose_name="Name (EN)")
    
    # ВИПРАВЛЕНО: Додано null=True та blank=True, щоб уникнути помилки 400 при збереженні без фото
    image = models.ImageField(
        upload_to='gallery/', 
        verbose_name="Зображення", 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ua or self.name_en

    class Meta:
        db_table = 'public_gallery'
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"