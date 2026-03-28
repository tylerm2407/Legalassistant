import { NextRequest, NextResponse } from "next/server";
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

    // Sync to Mailchimp
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
        // "Member Exists" is not an error — user already subscribed
        if (mailchimpError.title !== "Member Exists") {
          console.error("Mailchimp error:", mailchimpError);
        }
      }
    }

    // Write to Supabase as backup
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
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
        console.error("Supabase error:", supabaseError);
      }
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
