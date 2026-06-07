import os

path = r'd:\ua-art-galleries-backend-mainORIGIN\ua-art-galleries-backend-main\ua-art-galleries-backend-main\backend\mysite\app\utils\gemini_parser.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_method = '''    def extract_exhibition_links(self, page_text: str, base_url: str) -> dict:
        if not self.client:
            logger.error('GEMINI_API_KEY не знайдено.')
            return {'index_pages': [], 'exhibition_pages': []}
        if len(page_text) < 50:
            return {'index_pages': [], 'exhibition_pages': []}
        prompt = f"""
        Ти — веб-парсер арт-галерей.
        Твоє завдання: знайти у тексті всі потрібні посилання.
        Правила:
        1. Знайди посилання на ЗАГАЛЬНІ розділи виставок (наприклад, 'Виставки', 'Exhibitions', 'Past Shows', 'Архів', 'Current'). Поверни 1-2 найважливіших з них у масиві 'index_pages'.
        2. Також знайди всі прямі посилання на КОНКРЕТНІ окремі виставки і поверни їх у масиві 'exhibition_pages'.
        3. Усі посилання повинні бути абсолютними (починатись з http). Якщо посилання відносне — додай базовий URL: {base_url}
        4. ВІДПОВІДЬ: ТІЛЬКИ валідний JSON. Без тексту, без Markdown.
        Приклад:
        {{
            "index_pages": ["https://gallery.com/exhibitions"],
            "exhibition_pages": ["https://gallery.com/exhibition/spring-show"]
        }}
        Текст сторінки:
        ---
        {page_text[:10000]}
        ---
        """
        raw = self._call_gemini(prompt)
        if not raw:
            return {'index_pages': [], 'exhibition_pages': []}
        result = self._parse_list(raw)
        
        if isinstance(result, dict):
            return {
                'index_pages': [u for u in result.get('index_pages', []) if isinstance(u, str) and u.startswith('http')],
                'exhibition_pages': [u for u in result.get('exhibition_pages', []) if isinstance(u, str) and u.startswith('http')]
            }
        elif isinstance(result, list):
            return {'index_pages': [], 'exhibition_pages': [u for u in result if isinstance(u, str) and u.startswith('http')]}
        return {'index_pages': [], 'exhibition_pages': []}
'''

new_lines = lines[:94] + [new_method] + lines[128:]
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
