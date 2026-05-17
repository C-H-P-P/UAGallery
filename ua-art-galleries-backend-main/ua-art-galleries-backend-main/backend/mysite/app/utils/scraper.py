import requests
from bs4 import BeautifulSoup
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Клас для отримання тексту з сайтів галерей.
    """
    
    @staticmethod
    def fetch_text_from_url(url):
        """
        Завантажує HTML за посиланням і повертає очищений текст.
        Для Instagram/Facebook тимчасово повертає заглушку або використовує сторонній сервіс (Apify/ScrapingBee).
        """
        if 'instagram.com' in url or 'facebook.com' in url:
            # TODO: Для соцмереж потрібно використовувати API агрегаторів (напр. Apify).
            # Поки що повертаємо порожній рядок, щоб не блокували IP.
            logger.warning(f"Прямий скрапінг соцмереж ({url}) обмежений. Потрібен API-сервіс.")
            return ""
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Видаляємо скрипти, стилі, навігацію та футери
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
                
            # Отримуємо текст
            text = soup.get_text(separator=' ', strip=True)
            
            # Обмежуємо розмір тексту, щоб не переповнити контекст Gemini (приблизно перші 15000 символів)
            return text[:15000]
            
        except Exception as e:
            logger.error(f"Помилка скрапінгу {url}: {str(e)}")
            return ""

    @staticmethod
    def get_text_hash(text):
        """
        Створює MD5 хеш тексту для швидкого порівняння змін.
        """
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
