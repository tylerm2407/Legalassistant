import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/** Supabase project URL from environment variables. */
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";

/** Supabase anonymous (public) key for client-side authentication. */
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY ?? "";

/**
 * Singleton Supabase client for the CaseMate frontend.
 *
 * Uses lazy initialization to avoid crashing during static page generation
 * (e.g. on Render/Vercel) where env vars are not available at build time.
 * The client is only created when first accessed at runtime.
 */
let _supabase: SupabaseClient | null = null;

export const supabase: SupabaseClient = new Proxy({} as SupabaseClient, {
  get(_target, prop) {
    if (!_supabase) {
      if (!supabaseUrl || !supabaseKey) {
        throw new Error(
          "Supabase client accessed before env vars are available. " +
          "Ensure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_KEY are set."
        );
      }
      _supabase = createClient(supabaseUrl, supabaseKey);
    }
    return (_supabase as unknown as Record<string, unknown>)[prop as string];
  },
});
