// Translation Testing Utility
import i18n from '../i18n';

export const testTranslations = () => {
  const languages = ['es', 'en', 'pt'];
  const testKeys = [
    'app.name',
    'navigation.dashboard',
    'navigation.devices',
    'navigation.vehicles',
    'navigation.drivers',
    'navigation.reports',
    'navigation.monitoring',
    'navigation.settings',
    'login.title',
    'login.username',
    'login.password',
    'deviceManagement.title',
    'deviceManagement.addDevice',
    'deviceManagement.searchPlaceholder',
    'monitoring.title',
    'monitoring.realTimeStatus'
  ];

  console.log('🌐 Testing Translation Coverage');
  console.log('================================');

  languages.forEach(lang => {
    console.log(`\n📍 Testing ${lang.toUpperCase()}:`);
    
    // Change language temporarily
    i18n.changeLanguage(lang);
    
    testKeys.forEach(key => {
      const translation = i18n.t(key);
      const status = translation === key ? '❌ MISSING' : '✅ OK';
      console.log(`  ${key}: ${status} - "${translation}"`);
    });
  });

  console.log('\n✨ Translation test completed!');
};

export const getCurrentLanguageInfo = () => {
  return {
    currentLanguage: i18n.language,
    availableLanguages: Object.keys(i18n.store.data),
    isInitialized: i18n.isInitialized
  };
};

// Test function for real-time language switching
export const testLanguageSwitching = async () => {
  const languages = ['es', 'en', 'pt'];
  
  console.log('🔄 Testing Real-time Language Switching');
  console.log('======================================');
  
  for (const lang of languages) {
    console.log(`\n🌍 Switching to ${lang}...`);
    await i18n.changeLanguage(lang);
    
    // Wait for the change to propagate
    await new Promise(resolve => setTimeout(resolve, 100));
    
    console.log(`Current language: ${i18n.language}`);
    console.log(`App name: ${i18n.t('app.name')}`);
    console.log(`Dashboard: ${i18n.t('navigation.dashboard')}`);
    console.log(`Device Management: ${i18n.t('deviceManagement.title')}`);
  }
  
  console.log('\n✅ Language switching test completed!');
}; 