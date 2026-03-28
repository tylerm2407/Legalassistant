import { createClient } from "@supabase/supabase-js";

const supabaseUrl =
  process.env.EXPO_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseKey =
  process.env.EXPO_PUBLIC_SUPABASE_KEY || "placeholder";

export const supabase = createClient(supabaseUrl, supabaseKey);
