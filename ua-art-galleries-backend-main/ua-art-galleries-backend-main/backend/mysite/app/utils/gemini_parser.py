import os
import json
import logging
from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiParser:
    def __init__(self):
        self.model = os.environ.get('GEMINI_MODEL') or getattr(settings, 'GEMINI_MODEL', None)
        keys_str = os.environ.get('GEMINI_API_KEY', '')
        self.api_keys = [k.strip() for k in keys_str.split(',') if k.strip()]
        self.current_key_index = 0
        if self.api_keys:
            self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
        else:
            self.client = None

    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
        logger.warning(f"Перемикаємось на ключ #{self.current_key_index + 1}...")

    def _models_to_try(self):
        candidates = []
        if self.model:
            candidates.append(self.model.strip())
        for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            if m not in candidates:
                candidates.append(m)
        return candidates

    def _call_gemini(self, prompt: str) -> str | None:
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено.")
            return None

        max_keys = len(self.api_keys)

        for model_name in self._models_to_try():
            keys_tried = 0
            while keys_tried < max_keys:
                try:
                    logger.info(f"Gemini [{model_name}] ключ #{self.current_key_index + 1}")
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )
                    return getattr(response, "text", "") or ""
                except Exception as e:
                    msg = str(e).lower()
                    if "429" in msg or "403" in msg or "quota" in msg or "exhausted" in msg or "suspended" in msg:
                        keys_tried += 1
                        if keys_tried < max_keys:
                            self._rotate_key()
                        else:
                            logger.warning(f"Всі {max_keys} ключів вичерпали ліміти для {model_name}.")
                    else:
                        logger.error(f"Помилка моделі {model_name}: {e}")
                        break
        return None

    def _normalize_json_text(self, text: str) -> str:
        text = (text or "").strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _parse_list(self, raw: str) -> list:
        raw = self._normalize_json_text(raw)
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            start, end = raw.find("["), raw.rfind("]")
            if start != -1 and end > start:
                try:
                    payload = json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    return []
            else:
                return []
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            if "index_pages" in payload or "exhibition_pages" in payload:
                return payload
            for key in ("exhibitions", "urls", "links", "data"):
                if key in payload and isinstance(payload[key], list):
                    return payload[key]
        return []

    def extract_exhibition_links(self, page_text: str, base_url: str) -> dict:
        """
        Аналізує сторінку і повертає:
        {
          "parse_listing_directly": True/False,  -- якщо True, не треба ходити на підсторінки
          "index_pages": [...],                  -- загальні розділи (якщо моніторинг URL — головна)
          "exhibition_pages": [...],             -- прямі посилання на окремі виставки
        }

        Логіка вибору в run_detector:
          parse_listing_directly=True  → парсимо поточну сторінку напряму (економія запитів)
          exhibition_pages є           → заходимо тільки на ТІ сторінки
          index_pages є                → спочатку заходимо на розділ, потім повторно шукаємо
        """
        if not self.client:
            logger.error('GEMINI_API_KEY не знайдено.')
            return {'parse_listing_directly': False, 'index_pages': [], 'exhibition_pages': []}
        if len(page_text) < 50:
            return {'parse_listing_directly': False, 'index_pages': [], 'exhibition_pages': []}

        prompt = f"""
Ти — веб-парсер арт-галерей. Проаналізуй текст сторінки і визнач структуру.

Правила:
1. Якщо сторінка вже є СПИСКОМ виставок (містить назви + описи + дати кількох виставок одразу) — встанови "parse_listing_directly": true. Тоді підсторінки не потрібні.
2. Якщо сторінка — лише меню/головна без виставок — знайди посилання на розділ виставок у "index_pages" (1-2 URL).
3. Якщо сторінка має окремі посилання на КОНКРЕТНІ виставки — поверни їх у "exhibition_pages". Тільки посилання з числовим ID або чітким slug виставки.
4. Усі URL абсолютні. Відносні — доповни базовим URL: {base_url}
5. ВІДПОВІДЬ: тільки валідний JSON. Без тексту і Markdown.

Приклад для сторінки-списку (вже є дані):
{{"parse_listing_directly": true, "index_pages": [], "exhibition_pages": []}}

Приклад для головної сторінки без виставок:
{{"parse_listing_directly": false, "index_pages": ["https://gallery.com/exhibitions"], "exhibition_pages": []}}

Приклад для сторінки з посиланнями на конкретні виставки:
{{"parse_listing_directly": false, "index_pages": [], "exhibition_pages": ["https://gallery.com/exhibition/123-name"]}}

Базовий URL: {base_url}

Текст сторінки:
---
{page_text[:10000]}
---
"""
        raw = self._call_gemini(prompt)
        if not raw:
            return {'parse_listing_directly': False, 'index_pages': [], 'exhibition_pages': []}

        result = self._parse_list(raw)

        if isinstance(result, dict):
            return {
                'parse_listing_directly': bool(result.get('parse_listing_directly', False)),
                'index_pages': [u for u in result.get('index_pages', []) if isinstance(u, str) and u.startswith('http')],
                'exhibition_pages': [u for u in result.get('exhibition_pages', []) if isinstance(u, str) and u.startswith('http')],
            }
        elif isinstance(result, list):
            return {
                'parse_listing_directly': False,
                'index_pages': [],
                'exhibition_pages': [u for u in result if isinstance(u, str) and u.startswith('http')],
            }

        return {'parse_listing_directly': False, 'index_pages': [], 'exhibition_pages': []}

    def extract_exhibitions(self, text: str, gallery_name: str, max_exhibitions: int = 3) -> list[dict]:
        """
        Парсить текст і повертає список виставок.

        max_exhibitions: скільки максимум виставок повертати.
                         За замовчуванням 3 — лише актуальні/найновіші.
                         Передай None щоб знімати обмеження.
        """
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено. Парсинг неможливий.")
            return []
        if len(text) < 50:
            return []

        limit_instruction = (
            f"ВАЖЛИВО: поверни тільки {max_exhibitions} НАЙНОВІШІ або ПОТОЧНІ виставки. "
            f"Якщо виставок більше — бери ті з найпізнішою датою початку або ті що ще тривають."
            if max_exhibitions else
            "Знайди всі виставки."
        )

        prompt = f"""
Ти — професійний арт-куратор. Знайди інформацію про виставки
з тексту сторінки арт-галереї "{gallery_name}".
Текст сирий (веб-скрапінг), тому містить багато зайвого.

{limit_instruction}

Для кожної виставки визнач:
- "title": "Назва виставки" (рядок)
- "start_date": "YYYY-MM-DD" (якщо є день і місяць без року — додай поточний рік 2024, наприклад '5 травня' -> '2024-05-05'. Якщо дати немає — null)
- "end_date": "YYYY-MM-DD" (якщо немає — null)
- "image_url": абсолютний URL головного фото виставки з тексту (шукай ![alt](url) або src="..."). Якщо немає — null
- "description": короткий опис, 2-3 речення
- "artists": ["Ім'я Художника 1", ...]

Якщо виставок не знайдено — поверни [].
ВІДПОВІДЬ: ТІЛЬКИ валідний JSON масив. БЕЗ тегів і тексту.

Текст сторінки:
---
{text[:12000]}
---
"""
        raw = self._call_gemini(prompt)
        if not raw:
            return []

        result = self._parse_list(raw)
        exhibitions = [item for item in result if isinstance(item, dict) and item.get("title")]

        if max_exhibitions and len(exhibitions) > max_exhibitions:
            exhibitions = exhibitions[:max_exhibitions]

        return exhibitions
