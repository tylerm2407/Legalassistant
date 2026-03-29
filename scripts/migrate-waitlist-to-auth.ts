import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://bsszgxfkxxpgconmwczh.supabase.co";
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
});

async function migrate() {
  // 1. Fetch all Bryant emails from waitlist_signups
  const { data: signups, error: fetchError } = await supabase
    .from("waitlist_signups")
    .select("email")
    .like("email", "%@bryant.edu");

  if (fetchError) {
    console.error("Failed to fetch waitlist signups:", fetchError.message);
    process.exit(1);
  }

  console.log(`Found ${signups.length} Bryant emails to migrate.\n`);

  let created = 0;
  let skipped = 0;
  let failed = 0;

  for (const { email } of signups) {
    const { error } = await supabase.auth.admin.createUser({
      email,
      email_confirm: true,
      user_metadata: { source: "waitlist" },
    });

    if (error) {
      if (error.message.includes("already been registered")) {
        skipped++;
      } else {
        failed++;
        console.error(`  FAIL: ${email} — ${error.message}`);
      }
    } else {
      created++;
    }

    // Small delay to avoid rate limiting
    await new Promise((r) => setTimeout(r, 100));
  }

  console.log(`\nDone!`);
  console.log(`  Created: ${created}`);
  console.log(`  Skipped (already existed): ${skipped}`);
  console.log(`  Failed: ${failed}`);
}

migrate();
