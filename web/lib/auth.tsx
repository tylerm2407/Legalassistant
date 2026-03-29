"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "./supabase";

/**
 * Shape of the authentication context available throughout the CaseMate app.
 *
 * @property user - The currently authenticated Supabase user, or null if not logged in
 * @property session - The active Supabase session with JWT tokens, or null
 * @property loading - Whether the initial auth state is still being determined
 * @property signOut - Function to sign the user out and redirect to the auth page
 */
interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  loading: true,
  signOut: async () => {},
});

/**
 * Hook to access the current authentication state from any component.
 *
 * @returns The current auth context with user, session, loading state, and signOut function
 */
export function useAuth() {
  return useContext(AuthContext);
}

/** Routes that do not require authentication (landing page and auth page). */
const PUBLIC_PATHS = ["/auth", "/"];

/**
 * Authentication provider that wraps the CaseMate app with Supabase auth state.
 *
 * Manages the auth lifecycle: checks for existing sessions on mount, subscribes
 * to auth state changes, and redirects unauthenticated users to /auth for
 * protected routes. Provides user, session, and signOut via React context.
 *
 * @param props - Component props
 * @param props.children - Child components that will have access to auth context
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s);
      setUser(s?.user ?? null);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
      setUser(s?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (loading) return;
    const isPublic = PUBLIC_PATHS.some(
      (p) => pathname === p || pathname.startsWith(p + "/")
    );
    if (!user && !isPublic) {
      router.push("/auth");
    }
  }, [user, loading, pathname, router]);

  async function signOut() {
    await supabase.auth.signOut();
    router.push("/auth");
  }

  return (
    <AuthContext.Provider value={{ user, session, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
