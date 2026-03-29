import { createClient } from "@supabase/supabase-js";

/** Supabase project URL from environment variables. */
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;

/** Supabase anonymous (public) key for client-side authentication. */
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY!;

/**
 * Singleton Supabase client for the CaseMate frontend.
 *
 * Used for authentication (sign up, sign in, session management) and
 * as a fallback for direct database operations. The anonymous key limits
 * access to RLS-protected rows only.
 */
export const supabase = createClient(supabaseUrl, supabaseKey);
