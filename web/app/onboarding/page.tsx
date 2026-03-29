import OnboardingFlow from "@/components/OnboardingFlow";

/**
 * Onboarding page that renders the 5-step legal profile intake wizard.
 *
 * New users are directed here after authentication to build their initial
 * LegalProfile in Supabase before accessing the chat interface.
 */
export default function OnboardingPage() {
  return <OnboardingFlow />;
}
