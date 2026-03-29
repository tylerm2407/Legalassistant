/**
 * Next.js API route for CaseMate chat powered by OpenAI GPT-4o.
 *
 * Builds a personalized system prompt from the user's legal profile
 * (state, housing, employment, active issues, known facts) and streams
 * GPT-4o's response back to the client via Server-Sent Events.
 *
 * This is the memory injection pattern — the core differentiator of CaseMate.
 * Every response is personalized to the user's actual legal situation.
 */

import { NextRequest } from "next/server";
import OpenAI from "openai";

/** Legal area classification keywords. */
const LEGAL_AREA_KEYWORDS: Record<string, string[]> = {
  landlord_tenant: [
    "landlord", "tenant", "rent", "lease", "eviction", "deposit", "security deposit",
    "move-in", "move-out", "apartment", "housing", "mold", "repair", "habitability",
  ],
  employment: [
    "employer", "employee", "fired", "terminated", "wages", "overtime", "harassment",
    "discrimination", "workplace", "job", "salary", "hr", "unemployment", "worker",
  ],
  consumer: [
    "refund", "warranty", "scam", "fraud", "product", "defective", "return",
    "consumer", "purchase", "credit card", "charge", "billing",
  ],
  debt_collections: [
    "debt", "collector", "collection", "owe", "credit", "garnish", "repossess",
    "creditor", "default", "payment plan",
  ],
  small_claims: [
    "small claims", "sue", "lawsuit", "court", "damages", "claim", "judgment",
  ],
  contracts: [
    "contract", "agreement", "breach", "terms", "signed", "binding", "clause",
    "non-compete", "nda",
  ],
  traffic: [
    "ticket", "traffic", "speeding", "violation", "license", "dui", "dwi",
    "points", "driving",
  ],
  family_law: [
    "divorce", "custody", "child support", "alimony", "marriage", "prenup",
    "adoption", "guardianship", "will", "estate",
  ],
  criminal_records: [
    "expunge", "expungement", "criminal record", "seal", "conviction",
    "background check", "arrest",
  ],
  immigration: [
    "visa", "immigration", "green card", "citizenship", "deportation", "asylum",
    "work permit", "uscis",
  ],
};

/**
 * Classify a user's question into a legal area based on keyword matching.
 *
 * @param message - The user's message
 * @returns The classified legal area string
 */
function classifyLegalArea(message: string): string {
  const lower = message.toLowerCase();
  let bestArea = "general";
  let bestScore = 0;

  for (const [area, keywords] of Object.entries(LEGAL_AREA_KEYWORDS)) {
    const score = keywords.filter((kw) => lower.includes(kw)).length;
    if (score > bestScore) {
      bestScore = score;
      bestArea = area;
    }
  }

  return bestArea;
}

interface LegalIssue {
  issue_type: string;
  summary: string;
  status: string;
  notes: string[];
}

interface UserProfile {
  display_name: string;
  state: string;
  housing_situation: string;
  employment_type: string;
  family_status: string;
  language_preference: string;
  active_issues: LegalIssue[];
  legal_facts: string[];
}

/**
 * Build the CaseMate system prompt with full memory injection.
 *
 * This is the core of CaseMate — it makes every response personalized
 * to the user's state, housing, employment, active issues, and known facts.
 *
 * @param profile - The user's legal profile
 * @param legalArea - The classified legal area for this question
 * @returns Complete system prompt string for GPT-4o
 */
function buildSystemPrompt(profile: UserProfile, legalArea: string): string {
  const parts: string[] = [];

  parts.push(`You are CaseMate — a personalized legal assistant. You are the knowledgeable friend
that everyone deserves but few can afford. You give real, specific, actionable
legal guidance. You are NOT a licensed attorney and you make that clear when
relevant, but you do NOT hide behind that disclaimer to avoid giving real help.

USER'S LEGAL PROFILE:
- Name: ${profile.display_name}
- State: ${profile.state}
- Housing: ${profile.housing_situation}
- Employment: ${profile.employment_type}
- Family status: ${profile.family_status}`);

  // Active issues
  if (profile.active_issues && profile.active_issues.length > 0) {
    parts.push("\nACTIVE LEGAL ISSUES:");
    profile.active_issues.forEach((issue, i) => {
      parts.push(`\nIssue ${i + 1}: ${issue.issue_type.replace(/_/g, " ")}`);
      parts.push(`  Summary: ${issue.summary}`);
      parts.push(`  Status: ${issue.status}`);
      if (issue.notes && issue.notes.length > 0) {
        parts.push("  Key facts:");
        issue.notes.forEach((note) => parts.push(`    - ${note}`));
      }
    });
  }

  // Known legal facts
  if (profile.legal_facts && profile.legal_facts.length > 0) {
    parts.push("\nKNOWN LEGAL FACTS ABOUT THIS USER:");
    profile.legal_facts.forEach((fact) => parts.push(`- ${fact}`));
  }

  // Legal area context
  if (legalArea !== "general") {
    parts.push(`\nDETECTED LEGAL AREA: ${legalArea.replace(/_/g, " ")}`);
  }

  // Language preference
  if (profile.language_preference && profile.language_preference !== "en") {
    parts.push(`\nLANGUAGE: Respond entirely in ${profile.language_preference === "es" ? "Spanish" : profile.language_preference}. Translate legal terms but keep statute citations in their original language.`);
  }

  parts.push(`
RESPONSE RULES — follow these exactly:
1. Open by acknowledging what you already know about their situation.
   Never make them repeat context you already have.
2. Answer their specific question with their specific facts.
   Not a generic person's situation — theirs.
3. Cite the relevant statute for their state when it exists.
   Real citation (e.g. M.G.L. c.186 §15B), not vague references.
4. Tell them what they are ENTITLED TO, not just what the law says.
   Calculate damages if relevant. Name the specific remedy.
5. End with ONE concrete next step they can take TODAY.
   Not "you should consider..." — tell them what to do.
6. If a letter, rights summary, or checklist would help, offer to generate it.
7. Keep responses under 400 words unless the situation demands more.
   Dense, clear, actionable beats long and thorough.
8. Include this disclaimer at the end of substantive legal responses:
   "This is legal information, not legal advice. For advice specific to your situation, consult a licensed attorney in your state."`);

  return parts.join("\n");
}

interface ChatRequestBody {
  message: string;
  profile: UserProfile;
  history?: { role: string; content: string }[];
}

export async function POST(req: NextRequest) {
  try {
    const body: ChatRequestBody = await req.json();
    const { message, profile, history } = body;

    if (!message || !profile) {
      return new Response(
        JSON.stringify({ error: "Missing message or profile" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return new Response(
        JSON.stringify({ error: "OpenAI API key not configured" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const openai = new OpenAI({ apiKey });
    const legalArea = classifyLegalArea(message);
    const systemPrompt = buildSystemPrompt(profile, legalArea);

    // Build messages array with conversation history
    const messages: OpenAI.ChatCompletionMessageParam[] = [
      { role: "system", content: systemPrompt },
    ];

    if (history && history.length > 0) {
      for (const msg of history) {
        if (msg.role === "user" || msg.role === "assistant") {
          messages.push({ role: msg.role, content: msg.content });
        }
      }
    }

    messages.push({ role: "user", content: message });

    // Stream the response
    const stream = await openai.chat.completions.create({
      model: "gpt-4o",
      messages,
      max_tokens: 2048,
      stream: true,
    });

    // Create SSE response
    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const delta = chunk.choices[0]?.delta;
            if (delta?.content) {
              const event = JSON.stringify({ type: "token", content: delta.content });
              controller.enqueue(encoder.encode(`data: ${event}\n\n`));
            }
          }

          const done = JSON.stringify({ type: "done", legal_area: legalArea });
          controller.enqueue(encoder.encode(`data: ${done}\n\n`));
          controller.close();
        } catch (err) {
          const error = JSON.stringify({
            type: "error",
            message: err instanceof Error ? err.message : "Stream failed",
          });
          controller.enqueue(encoder.encode(`data: ${error}\n\n`));
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ error: err instanceof Error ? err.message : "Internal error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
