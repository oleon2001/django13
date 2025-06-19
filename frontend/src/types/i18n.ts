// Import the resources to enable strong typing
import 'react-i18next';

declare module 'react-i18next' {
  interface CustomTypeOptions {
    // Define the default namespace as 'translation'
    defaultNS: 'translation';
    
    // Make the translations strongly typed
    resources: {
      translation: any;
    };
  }
}

export interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag?: string;
}

export const availableLanguages: Language[] = [
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português' },
];

export default availableLanguages; 