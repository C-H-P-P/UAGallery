import os
import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiParser:
    """
    Клас для взаємодії з Google Gemini API (модель gemini-1.5-flash).
    Використовується для витягування структурованих даних (JSON) з сирого тексту сайтів.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Використовуємо дешеву та швидку модель
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def extract_exhibitions(self, text, gallery_name):
        """
        Відправляє текст до Gemini і просить повернути масив виставок у форматі JSON.
        """
        if not self.model:
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
4. ТВОЯ ВІДПОВІДЬ ПОВИННА БУТИ ВИКЛЮЧНО ВАЛІДНИМ JSON МАСИВОМ ОБ'ЄКТІВ. БЕЗ ЖОДНИХ ТЕГІВ ```json ТА ІНШОГО ТЕКСТУ.

Ось текст сторінки:
---
{text[:12000]}
---
"""
        try:
            # Налаштування generation_config для вимоги JSON (підтримується в нових версіях)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1, # Низька температура для більш точних і передбачуваних результатів
                )
            )
            
            response_text = response.text.strip()
            
            # Очищення від маркдауну, якщо Gemini все ж його додала
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            response_text = response_text.strip()
            
            # Парсимо JSON
            exhibitions_data = json.loads(response_text)
            
            if isinstance(exhibitions_data, list):
                return exhibitions_data
            elif isinstance(exhibitions_data, dict) and "exhibitions" in exhibitions_data:
                return exhibitions_data["exhibitions"]
            else:
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Помилка парсингу JSON від Gemini: {str(e)}\nВідповідь: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Помилка виклику Gemini API: {str(e)}")
            return []
