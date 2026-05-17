import os
import google.generativeai as genai

# Тестовий текст (ніби ми скрапером стягнули його з сайту галереї)
TEST_TEXT = """
Запрошуємо на відкриття нової виставки "Тіні забутих предків"!
Відкриття відбудеться 25 травня 2026 року о 18:00 в нашій галереї.
Виставка триватиме до 15 червня 2026 року.
На виставці будуть представлені нові роботи видатних українських митців: Івана Марчука та Марії Примаченко.
Це унікальна можливість побачити поєднання класики та сучасності.
Чекаємо на вас за адресою: вул. Хрещатик, 15. Вхід вільний.
"""

def run_test():
    # Отримуємо ключ
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("ПОМИЛКА: Не знайдено GEMINI_API_KEY у змінних середовища.")
        print("Для локального тесту запустіть: $env:GEMINI_API_KEY='ваш_ключ'; python test_ai.py")
        return

    print("Підключення до Gemini AI...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
Ти професійний арт-куратор. Знайди інформацію про виставки.
Поверни ВАЛІДНИЙ JSON масив об'єктів. БЕЗ тегів ```json.
Поля: title, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), description, artists (масив).

Текст:
{TEST_TEXT}
"""
    
    print("Відправка запиту...")
    try:
        response = model.generate_content(prompt)
        print("\n--- ВІДПОВІДЬ ВІД AI (JSON) ---")
        print(response.text.strip())
        print("-------------------------------")
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    run_test()
