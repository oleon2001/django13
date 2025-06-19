import { useTranslation } from 'react-i18next';
import { useCallback, useEffect } from 'react';

export const useLanguage = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = useCallback(async (newLanguage: string) => {
    try {
      await i18n.changeLanguage(newLanguage);
      
      localStorage.setItem('selectedLanguage', newLanguage);
      
      window.dispatchEvent(new StorageEvent('storage', {
        key: 'selectedLanguage',
        newValue: newLanguage,
        storageArea: localStorage
      }));
      
      console.log(`Language changed to: ${newLanguage}`);
    } catch (error) {
      console.error('Error changing language:', error);
    }
  }, [i18n]);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'selectedLanguage' && e.newValue && e.newValue !== i18n.language) {
        i18n.changeLanguage(e.newValue);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
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
    currentLanguage: i18n.language,
    changeLanguage,
    getCurrentLanguage,
    getLanguageNames,
    getAvailableLanguages,
    availableLanguages: ['es', 'en', 'pt'],
    isReady: i18n.isInitialized,
    t,
  };
};

export default useLanguage; 