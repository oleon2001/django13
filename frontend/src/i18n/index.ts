import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation resources
import { translations } from './resources';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: translations,
    lng: localStorage.getItem('selectedLanguage') || 'es', // default language
    fallbackLng: 'es', // use es if detected lng is not available

    keySeparator: '.',
    interpolation: {
      escapeValue: false, // react already does escaping
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'selectedLanguage',
    },
  });

export default i18n; 