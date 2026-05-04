import { createContext, useContext, useState, useEffect } from 'react';
import { DICT } from '../i18n/translations';

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [siteLang, setSiteLang] = useState(() => localStorage.getItem('layrpdf-lang') || 'pt');

  useEffect(() => {
    localStorage.setItem('layrpdf-lang', siteLang);
  }, [siteLang]);

  const t = DICT[siteLang] || DICT['pt'];

  return (
    <LanguageContext.Provider value={{ siteLang, setSiteLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
