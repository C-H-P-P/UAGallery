import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import translationUK from './locales/uk/translation.json';
import translationEN from './locales/en/translation.json';

// Отримуємо збережену мову або встановлюємо дефолтну
const savedLanguage = localStorage.getItem('language') || 'uk';

const resources = {
    en: {
        translation: translationEN,
    },
    uk: {
        translation: translationUK,
    },
};

i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: savedLanguage, // мова за замовчуванням
        fallbackLng: 'en',  // мова, якщо переклад не знайдено
        interpolation: {
            escapeValue: false, // react вже екранує значення
        },
    });

export default i18n;
