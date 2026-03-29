import { redirect } from "next/navigation";

/**
 * Root landing page that redirects to the authentication page.
 *
 * Server-side redirect ensures unauthenticated users land on /auth
 * and authenticated users are routed through the auth flow to /chat.
 */
export default function HomePage() {
  redirect("/auth");
}
