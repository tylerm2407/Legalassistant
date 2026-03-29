import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase";
import { createClient } from "@supabase/supabase-js";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, source = "landing_page" } = body;

    if (!email || typeof email !== "string" || !EMAIL_REGEX.test(email.trim())) {
      return NextResponse.json(
        { error: "Please enter a valid email address." },
        { status: 400 }
      );
    }

    const normalizedEmail = email.trim().toLowerCase();

    // 1. Sync to Mailchimp (if configured)
    const mailchimpApiKey = process.env.MAILCHIMP_API_KEY;
    const mailchimpServer = process.env.MAILCHIMP_SERVER_PREFIX;
    const mailchimpListId = process.env.MAILCHIMP_LIST_ID;

    if (mailchimpApiKey && mailchimpServer && mailchimpListId) {
      const mailchimpUrl = `https://${mailchimpServer}.api.mailchimp.com/3.0/lists/${mailchimpListId}/members`;

      const mailchimpRes = await fetch(mailchimpUrl, {
        method: "POST",
        headers: {
          Authorization: `apikey ${mailchimpApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email_address: normalizedEmail,
          status: "subscribed",
          tags: ["waitlist", source],
        }),
      });

      if (!mailchimpRes.ok) {
        const mailchimpError = await mailchimpRes.json();
        if (mailchimpError.title !== "Member Exists") {
          console.error("Mailchimp error:", mailchimpError);
        }
      }
    }

    // 2. Upsert into waitlist_signups table
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (supabaseUrl && supabaseAnonKey) {
      const supabase = createClient(supabaseUrl, supabaseAnonKey);

      const { error: supabaseError } = await supabase
        .from("waitlist_signups")
        .upsert(
          { email: normalizedEmail, source, mailchimp_synced: !!mailchimpApiKey },
          { onConflict: "email" }
        );

      if (supabaseError) {
        console.error("Supabase waitlist error:", supabaseError);
      }
    }

    // 3. Create Supabase Auth account (so user can log in to the main app)
    try {
      const supabaseAdmin = createAdminClient();

      const { error: authError } = await supabaseAdmin.auth.admin.createUser({
        email: normalizedEmail,
        email_confirm: false, // They'll get a confirmation email from Supabase
        user_metadata: { source: "waitlist" },
      });

      // Ignore "user already exists" errors — that's fine
      if (authError && !authError.message.includes("already been registered")) {
        console.error("Auth account creation error:", authError);
      }
    } catch (authErr) {
      // Don't fail the entire request if auth account creation fails
      console.error("Auth account creation failed:", authErr);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Waitlist signup error:", error);
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    );
  }
}
