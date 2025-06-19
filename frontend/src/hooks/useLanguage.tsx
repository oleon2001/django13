import { useTranslation } from 'react-i18next';
import { useCallback } from 'react';

export const useLanguage = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = useCallback((language: string) => {
    i18n.changeLanguage(language);
    // Save to localStorage for persistence
    localStorage.setItem('selectedLanguage', language);
  }, [i18n]);

  const getCurrentLanguage = useCallback(() => {
    return i18n.language;
  }, [i18n.language]);

  const getLanguageNames = useCallback(() => {
    return {
      es: t('configuration.languages.es'),
      en: t('configuration.languages.en'),
      pt: t('configuration.languages.pt'),
    };
  }, [t]);

  const getAvailableLanguages = useCallback(() => {
    return [
      { code: 'es', name: t('configuration.languages.es') },
      { code: 'en', name: t('configuration.languages.en') },
      { code: 'pt', name: t('configuration.languages.pt') },
    ];
  }, [t]);

  return {
    changeLanguage,
    getCurrentLanguage,
    getLanguageNames,
    getAvailableLanguages,
    currentLanguage: i18n.language,
    t,
  };
};

export default useLanguage; 