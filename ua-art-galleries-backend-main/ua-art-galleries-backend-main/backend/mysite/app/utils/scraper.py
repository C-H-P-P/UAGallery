import requests
from bs4 import BeautifulSoup
import logging
import hashlib
import json
import os
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Клас для отримання тексту з сайтів галерей.
    """
    
    @staticmethod
    def fetch_text_from_url(url, return_error=False):
        """
        Завантажує HTML за посиланням і повертає очищений текст.
        Для Instagram/Facebook тимчасово повертає заглушку або використовує сторонній сервіс (Apify/ScrapingBee).
        """
        try:
            if not url:
                return ("", "empty url") if return_error else ""
            url = url.strip()
            if not url:
                return ("", "empty url") if return_error else ""
            if url.startswith("`") and url.endswith("`"):
                url = url[1:-1].strip()
            if "http" in url and not url.startswith(("http://", "https://")):
                start = url.find("http")
                if start != -1:
                    url = url[start:].strip().strip("`").strip()
            url = url.strip().strip(")").strip("]").strip("}").strip(",").strip(".").strip("`").strip()
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            is_social = "instagram.com" in url or "facebook.com" in url
            proxy_template = os.environ.get("SCRAPER_TEXT_PROXY") or (
                "https://r.jina.ai/{url}" if os.environ.get("SCRAPER_USE_JINA") == "1" else None
            )
            if is_social and not proxy_template:
                logger.warning(f"Прямий скрапінг соцмереж ({url}) обмежений. Потрібен API-сервіс або проксі.")
                return ("", "social scraping blocked") if return_error else ""

            parsed = urlparse(url)
            referer = f"{parsed.scheme}://{parsed.netloc}/" if parsed.scheme and parsed.netloc else None

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Upgrade-Insecure-Requests": "1",
            }
            if referer:
                headers["Referer"] = referer

            session = requests.Session()
            retries = Retry(
                total=2,
                connect=2,
                read=2,
                backoff_factor=0.8,
                status_forcelist=(403, 408, 425, 429, 500, 502, 503, 504),
                allowed_methods=("GET",),
                raise_on_status=False,
            )
            session.mount("http://", HTTPAdapter(max_retries=retries))
            session.mount("https://", HTTPAdapter(max_retries=retries))

            response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
            response.raise_for_status()
            
            content_type = (response.headers.get("Content-Type") or "").lower()
            if "text/plain" in content_type and response.text:
                text = response.text.strip()[:15000]
                return (text, None) if return_error else text

            soup = BeautifulSoup(response.content, "html.parser")
            
            # Видаляємо скрипти, стилі, навігацію та футери
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
                
            # Отримуємо текст
            text = soup.get_text(separator=' ', strip=True)
            
            # Обмежуємо розмір тексту, щоб не переповнити контекст Gemini (приблизно перші 15000 символів)
            text = text[:15000]
            return (text, None) if return_error else text
            
        except Exception as e:
            try:
                if proxy_template and url:
                    proxied_url = proxy_template.format(url=url)
                    response = requests.get(proxied_url, timeout=25)
                    response.raise_for_status()
                    text = (response.text or "").strip()[:15000]
                    return (text, None) if return_error else text
            except Exception:
                pass

            logger.error(f"Помилка скрапінгу {url}: {str(e)}")
            return ("", str(e)) if return_error else ""

    @staticmethod
    def get_text_hash(text):
        """
        Створює MD5 хеш тексту для швидкого порівняння змін.
        """
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
