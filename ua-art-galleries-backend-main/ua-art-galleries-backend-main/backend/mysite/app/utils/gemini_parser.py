import os
import json
import logging
from google import genai
from google.genai import types
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiParser:
    """
    Клас для взаємодії з Google Gemini API через новий пакет google-genai.
    """
    
    def __init__(self):
        self.model = os.environ.get('GEMINI_MODEL') or getattr(settings, 'GEMINI_MODEL', None)
        keys_str = os.environ.get('GEMINI_API_KEY', '')
        self.api_keys = [k.strip() for k in keys_str.split(',') if k.strip()]
        self.current_key_index = 0
        if self.api_keys:
            self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
        else:
            self.client = None
    
    def _model_candidates(self):
        candidates = []
        if self.model:
            candidates.append(self.model)
        candidates.extend([
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
        ])
        seen = set()
        out = []
        for c in candidates:
            if not c:
                continue
            c = c.strip()
            if not c:
                continue
            if c not in seen:
                out.append(c)
                seen.add(c)
        return out
    
    def _normalize_response_text(self, response_text):
        response_text = (response_text or "").strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        return response_text.strip()
    
    def _parse_json_payload(self, response_text):
        response_text = self._normalize_response_text(response_text)
        if not response_text:
            return []
        try:
            payload = json.loads(response_text)
        except json.JSONDecodeError:
            start = response_text.find("[")
            end = response_text.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    payload = json.loads(response_text[start : end + 1])
                except json.JSONDecodeError:
                    payload = None
            else:
                payload = None
        
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and "exhibitions" in payload and isinstance(payload["exhibitions"], list):
            return payload["exhibitions"]
        return []

    def extract_exhibitions(self, text, gallery_name):
        """
        Відправляє текст до Gemini і просить повернути масив виставок у форматі JSON.
        """
        if not self.client:
            logger.error("GEMINI_API_KEY не знайдено. Парсинг неможливий.")
            return []
            
        if len(text) < 50:
            return []

        prompt = f"""
Ти професійний арт-куратор. Твоє завдання - знайти інформацію про поточні або майбутні виставки з тексту сторінки арт-галереї "{gallery_name}".
Текст сирий, отриманий через веб-скрапінг, тому містить багато сміття.

Правила:
1. Знайди всі анонси виставок або мистецьких подій.
2. Для кожної виставки визнач:
   - title (Назва виставки, рядок)
   - start_date (Дата початку у форматі YYYY-MM-DD, або null якщо не знайдено)
   - end_date (Дата завершення у форматі YYYY-MM-DD, або null якщо не знайдено)
   - description (Короткий опис, 2-3 речення)
   - artists (Масив імен художників, які беруть участь)
3. Якщо виставок не знайдено, поверни порожній масив [].
4. ТВОЯ ВІДПОВІДЬ ПОВИННА БУТИ ВИКЛЮЧНО ВАЛІДНИМ JSON МАСИВОМ ОБ'ЄКТІВ. БЕЗ ЖОДНИХ ТЕГІВ ТА ІНШОГО ТЕКСТУ.

Ось текст сторінки:
---
{text[:12000]}
---
"""
        try:
            prompt = self.base_prompt.replace("{gallery_name}", gallery_name).replace("{text}", text[:12000])
            
            # Спроба з різними моделями, починаючи з найшвидшої
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-1.5-flash',
                'gemini-1.5-pro'
            ]
            
            for model_name in models_to_try:
                # Зберігаємо скільки ключів ми вже спробували для цієї моделі
                keys_tried = 0
                max_keys = len(self.api_keys)
                
                while keys_tried < max_keys:
                    try:
                        logger.info(f"Спроба використання моделі {model_name} з ключем #{self.current_key_index + 1}")
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=self.generation_config,
                        )
                        
                        exhibitions_data = self._parse_json_payload(getattr(response, "text", ""))
                        
                        # Якщо парсинг успішний (навіть якщо це порожній список [])
                        if exhibitions_data is not None:
                            return exhibitions_data
                            
                        # Якщо AI повернув щось незрозуміле, спробуємо іншу модель
                        break
                        
                    except Exception as e:
                        msg = str(e).lower()
                        if "429" in msg or "quota" in msg or "exhausted" in msg:
                            keys_tried += 1
                            if keys_tried < max_keys:
                                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                                self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
                                logger.warning(f"Ліміт або 429. Перемикаємось на ключ #{self.current_key_index + 1}...")
                                continue
                            else:
                                logger.error(f"Всі {max_keys} ключів вичерпали ліміти для {model_name}!")
                                break # Переходимо до наступної моделі
                        else:
                            logger.error(f"Помилка моделі {model_name}: {str(e)}")
                            break # Переходимо до наступної моделі
            
            return []
            
        except Exception as e:
            logger.error(f"Помилка виклику Gemini API: {str(e)}")
            return []
