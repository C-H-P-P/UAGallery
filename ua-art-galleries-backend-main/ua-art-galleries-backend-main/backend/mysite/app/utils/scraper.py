import requests
from bs4 import BeautifulSoup
import logging
import hashlib
import os
import time
import re
from urllib.parse import urlparse, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
logger = logging.getLogger(__name__)
class WebScraper:
    @staticmethod
    def fetch_text_from_url(url, return_error=False):
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
                logger.warning(f"Прямий скрапінг соцмереж ({url}) заблоковано. Використовуй InstagramScraper/FacebookScraper.")
                return ("", "social scraping blocked") if return_error else ""
            if is_social and proxy_template:
                proxied_url = proxy_template.format(url=url)
                resp = requests.get(proxied_url, timeout=25)
                resp.raise_for_status()
                text = (resp.text or "").strip()[:15000]
                return (text, None) if return_error else text
            parsed = urlparse(url)
            referer = f"{parsed.scheme}://{parsed.netloc}/" if parsed.scheme and parsed.netloc else None
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Upgrade-Insecure-Requests": "1",
            }
            if referer:
                headers["Referer"] = referer
            session = requests.Session()
            retries = Retry(
                total=2, connect=2, read=2, backoff_factor=0.8,
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
                text = response.text.strip()[:40000]
                return (text, None) if return_error else text
            soup = BeautifulSoup(response.content, "html.parser")
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            for img in soup.find_all('img'):
                src = img.get('src', '').strip()
                alt = img.get('alt', '').strip()
                if src and not src.startswith('data:'):
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(url, src)
                    img.replace_with(f" ![{alt}]({src}) ")

            text = soup.get_text(separator=' ', strip=True)
            text_without_images = re.sub(r'!\[.*?\]\(.*?\)', '', text)
            proxy_template = os.environ.get("SCRAPER_TEXT_PROXY") or "https://r.jina.ai/{url}"
            if len(text_without_images) < 1500 and proxy_template:
                proxied_url = proxy_template.format(url=url)
                resp = requests.get(proxied_url, timeout=25)
                if resp.status_code == 200:
                    text = (resp.text or "").strip()
            text = text[:40000]
            return (text, None) if return_error else text
        except Exception as e:
            try:
                proxy_template = os.environ.get("SCRAPER_TEXT_PROXY") or "https://r.jina.ai/{url}"
                if proxy_template and url:
                    proxied_url = proxy_template.format(url=url)
                    resp = requests.get(proxied_url, timeout=25)
                    resp.raise_for_status()
                    text = (resp.text or "").strip()[:40000]
                    return (text, None) if return_error else text
            except Exception:
                pass
            logger.error(f"Помилка скрапінгу {url}: {e}")
            return ("", str(e)) if return_error else ""
    @staticmethod
    def get_text_hash(text):
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
class PlaywrightScraper:
    @staticmethod
    def fetch_text_from_url(url: str, wait_for: str = "networkidle", timeout: int = 30000) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error(
                "Playwright не встановлено. Виконай: "
                "pip install playwright && playwright install chromium --with-deps"
            )
            return ""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-setuid-sandbox",
                ])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/124.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                try:
                    page.goto(url, wait_until=wait_for, timeout=timeout)
                except Exception:
                    pass
                page.evaluate("""
                    document.querySelectorAll('nav, footer, header, script, style')
                              .forEach(el => el.remove());
                """)
                text = page.inner_text("body") or ""
                browser.close()
                return text[:15000]
        except Exception as e:
            logger.error(f"PlaywrightScraper помилка для {url}: {e}")
            return ""
    @staticmethod
    def get_text_hash(text: str) -> str:
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
class InstagramScraper:
    @staticmethod
    def _extract_username_from_url(url: str) -> str:
        try:
            path = urlparse(url).path.strip("/")
            username = path.split("/")[0]
            return username if username else ""
        except Exception:
            return ""
    @staticmethod
    def fetch_posts(username_or_url: str, max_posts: int = 15) -> str:
        try:
            import instaloader
        except ImportError:
            logger.error("Instaloader не встановлено. Виконай: pip install instaloader")
            return ""
        username = username_or_url.strip().lstrip("@")
        if username.startswith("http"):
            username = InstagramScraper._extract_username_from_url(username)
        if not username:
            logger.error(f"Не вдалося визначити Instagram username з: {username_or_url}")
            return ""
        try:
            L = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                quiet=True,
            )
            ig_user = os.environ.get('INSTAGRAM_USER')
            ig_pass = os.environ.get('INSTAGRAM_PASS')
            if ig_user and ig_pass:
                try:
                    L.login(ig_user, ig_pass)
                    logger.info(f"Instagram: залогінено як {ig_user}")
                except Exception as login_err:
                    logger.warning(f"Instagram login failed: {login_err}. Продовжуємо без логіну.")
            profile = instaloader.Profile.from_username(L.context, username)
            posts_text = []
            for i, post in enumerate(profile.get_posts()):
                if i >= max_posts:
                    break
                caption = (post.caption or "").strip()
                if not caption:
                    continue
                date_str = post.date.strftime("%Y-%m-%d") if post.date else "невідома дата"
                posts_text.append(f"[Пост від {date_str}]\n{caption}")
                if i > 0 and i % 5 == 0:
                    time.sleep(2)
            if not posts_text:
                logger.warning(f"Instagram @{username}: постів з текстом не знайдено")
                return ""
            result = "\n\n---\n\n".join(posts_text)
            logger.info(f"Instagram @{username}: отримано {len(posts_text)} постів")
            return result
        except Exception as e:
            logger.error(f"InstagramScraper помилка для @{username}: {e}")
            return ""
    @staticmethod
    def get_text_hash(text: str) -> str:
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
class FacebookScraper:
    @staticmethod
    def _extract_page_id_from_url(url: str) -> str:
        try:
            path = urlparse(url).path.strip("/")
            page_id = path.split("/")[0]
            return page_id if page_id else ""
        except Exception:
            return ""
    @staticmethod
    def _via_graph_api(page_id: str, token: str, max_posts: int = 15) -> str:
        try:
            api_url = (
                f"https://graph.facebook.com/v19.0/{page_id}/posts"
                f"?fields=message,story,created_time"
                f"&limit={max_posts}"
                f"&access_token={token}"
            )
            resp = requests.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            posts = data.get("data", [])
            if not posts:
                logger.warning(f"Facebook Graph API: постів не знайдено для {page_id}")
                return ""
            posts_text = []
            for post in posts:
                text = (post.get("message") or post.get("story") or "").strip()
                if not text:
                    continue
                date = post.get("created_time", "")[:10]
                posts_text.append(f"[Пост від {date}]\n{text}")
            result = "\n\n---\n\n".join(posts_text)
            logger.info(f"Facebook Graph API: отримано {len(posts_text)} постів для {page_id}")
            return result
        except Exception as e:
            logger.error(f"Facebook Graph API помилка для {page_id}: {e}")
            return ""
    @staticmethod
    def _via_playwright(url: str) -> str:
        logger.warning(
            f"FacebookScraper: використовується Playwright для {url}. "
            "Рекомендовано налаштувати FACEBOOK_ACCESS_TOKEN."
        )
        try:
            text = PlaywrightScraper.fetch_text_from_url(url, wait_for="domcontentloaded")
            if len(text) < 100:
                logger.warning(f"Facebook Playwright: отримано замало тексту ({len(text)} символів). "
                               "Можливо заблоковано.")
            return text
        except Exception as e:
            logger.error(f"FacebookScraper Playwright помилка: {e}")
            return ""
    @staticmethod
    def fetch_posts(url: str, max_posts: int = 15) -> str:
        fb_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        if fb_token:
            page_id = FacebookScraper._extract_page_id_from_url(url)
            if not page_id:
                logger.error(f"Не вдалося визначити Facebook page_id з: {url}")
                return ""
            return FacebookScraper._via_graph_api(page_id, fb_token, max_posts)
        else:
            logger.warning(
                "FACEBOOK_ACCESS_TOKEN не знайдено. "
                "Використовується Playwright (менш надійно). "
                "Додай токен в env для стабільної роботи."
            )
            return FacebookScraper._via_playwright(url)
    @staticmethod
    def get_text_hash(text: str) -> str:
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
