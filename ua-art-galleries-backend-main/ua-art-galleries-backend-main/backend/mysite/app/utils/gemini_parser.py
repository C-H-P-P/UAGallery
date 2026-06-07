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
        for m in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
            if m not in candidates:
                candidates.append(m)
        return candidates
    def _call_gemini(self, prompt: str) -> str | None:
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено.")
            return None
        for model_name in self._models_to_try():
            keys_tried = 0
            max_keys = len(self.api_keys)
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
                    if "429" in msg or "quota" in msg or "exhausted" in msg:
                        keys_tried += 1
                        if keys_tried < max_keys:
                            self._rotate_key()
                            continue
                        else:
                            logger.error(f"Всі {max_keys} ключів вичерпали ліміти для {model_name}.")
                            break
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
            for key in ("exhibitions", "urls", "links", "data"):
                if key in payload and isinstance(payload[key], list):
                    return payload[key]
        return []
    def extract_exhibition_links(self, page_text: str, base_url: str) -> list[str]:
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено.")
            return []
        if len(page_text) < 50:
            return []
        prompt = f"""
Ти — парсер веб-сторінок арт-галерей.
Твоє завдання: знайти у тексті нижче всі посилання (URL), що ведуть на ОКРЕМІ сторінки виставок.
Правила:
1. Шукай посилання з патернами: /exhibition/, /vystavka/, /event/, /shows/, /expo/ тощо.
2. Повертай лише посилання на КОНКРЕТНІ виставки, НЕ на розділи (не /exhibitions/, не /events/).
3. Якщо посилання відносне (наприклад /exhibition/vin) — перетвори в абсолютне, використовуючи базовий URL: {base_url}
4. Якщо на сторінці вже є ПОВНІ описи виставок (назва + дата + опис) без потреби переходити на підсторінки — поверни порожній масив [].
5. Якщо посилань на підсторінки не знайдено — поверни порожній масив [].
6. ВІДПОВІДЬ: ТІЛЬКИ валідний JSON масив рядків. Без пояснень, без тегів.
Приклад правильної відповіді:
["https://gallery.com/exhibition/spring-show", "https://gallery.com/exhibition/art-2024"]
Базовий URL галереї: {base_url}
Текст сторінки:
---
{page_text[:8000]}
---
"""
        raw = self._call_gemini(prompt)
        if not raw:
            return []
        result = self._parse_list(raw)
        urls = []
        for item in result:
            if isinstance(item, str) and item.startswith("http"):
                urls.append(item.strip())
        logger.info(f"extract_exhibition_links: знайдено {len(urls)} посилань для {base_url}")
        return urls
    def extract_exhibitions(self, text: str, gallery_name: str) -> list[dict]:
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено. Парсинг неможливий.")
            return []
        if len(text) < 50:
            return []
        prompt = f"""
Ти — професійний арт-куратор. Знайди інформацію про поточні або майбутні виставки
з тексту сторінки арт-галереї "{gallery_name}".
Текст сирий (веб-скрапінг), тому містить багато зайвого.
Правила:
1. Знайди всі анонси виставок або мистецьких подій.
2. Для кожної виставки визнач:
   - title       (Назва виставки, рядок)
   - start_date  (Дата початку СУВОРО у форматі YYYY-MM-DD. Якщо невідома — null)
   - end_date    (Дата завершення СУВОРО у форматі YYYY-MM-DD. Якщо невідома — null)
   - description (Короткий опис, 2-3 речення)
   - artists     (Масив імен художників)
3. Якщо виставок не знайдено — поверни порожній масив [].
4. ВІДПОВІДЬ: ВИКЛЮЧНО валідний JSON масив об'єктів. БЕЗ тегів та іншого тексту.
Текст сторінки:
---
{text[:12000]}
---
"""
        raw = self._call_gemini(prompt)
        if not raw:
            return []
        result = self._parse_list(raw)
        exhibitions = []
        for item in result:
            if isinstance(item, dict) and item.get("title"):
                exhibitions.append(item)
        return exhibitions
