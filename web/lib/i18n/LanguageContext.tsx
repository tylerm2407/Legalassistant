"use client";

/**
 * Language context and translation hook for CaseMate's English/Spanish UI.
 *
 * Wraps the app in a LanguageProvider that reads `language_preference` from
 * the user's profile. Components call `useTranslation()` to get the `t()`
 * helper, which returns the correct string for the active locale.
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from "react";
import translations, { type Locale, type TranslationKey } from "./translations";

interface LanguageContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  locale: "en",
  setLocale: () => {},
  t: (key) => {
    const entry = translations[key];
    if (typeof entry === "object" && "en" in entry) {
      const val = entry.en;
      return typeof val === "string" ? val : "";
    }
    return key;
  },
});

interface LanguageProviderProps {
  initialLocale?: Locale;
  children: React.ReactNode;
}

/**
 * Provides language state and translation function to the entire app.
 *
 * @param props.initialLocale - Starting locale, typically from the user's profile
 * @param props.children - App content
 */
export function LanguageProvider({ initialLocale = "en", children }: LanguageProviderProps) {
  const [locale, setLocale] = useState<Locale>(initialLocale);

  const t = useCallback(
    (key: TranslationKey): string => {
      const entry = translations[key];
      if (!entry) return key;
      if (typeof entry === "object" && locale in entry) {
        const val = (entry as Record<Locale, unknown>)[locale];
        return typeof val === "string" ? val : "";
      }
      return key;
    },
    [locale]
  );

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, t]);

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

/**
 * Hook to access the current locale and translation function.
 *
 * @returns `{ locale, setLocale, t }` where `t(key)` returns the translated string.
 */
export function useTranslation() {
  return useContext(LanguageContext);
}

export { LanguageContext };
