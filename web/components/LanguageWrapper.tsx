"use client";

/**
 * Top-level client wrapper that reads the user's language preference and
 * provides it via LanguageProvider to the entire app.
 *
 * Fetches language_preference from the user's profile on mount and updates
 * the LanguageProvider when it changes. Pages that already have the profile
 * loaded (e.g. ChatInterface) can call `setLocale()` directly when the
 * sidebar toggle fires.
 */

import React, { useEffect, useState } from "react";
import { LanguageProvider, type Locale } from "@/lib/i18n";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";

interface LanguageWrapperProps {
  children: React.ReactNode;
}

export default function LanguageWrapper({ children }: LanguageWrapperProps) {
  const { user, loading: authLoading } = useAuth();
  const [locale, setLocale] = useState<Locale>("en");

  useEffect(() => {
    if (authLoading || !user) return;

    async function fetchLang() {
      try {
        const profile = await api.getProfile(user!.id);
        if (profile?.language_preference === "es") {
          setLocale("es");
        }
      } catch {
        // Default to English on error
      }
    }
    fetchLang();
  }, [user, authLoading]);

  return (
    <LanguageProvider initialLocale={locale} key={locale}>
      {children}
    </LanguageProvider>
  );
}
