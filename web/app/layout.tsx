import type { Metadata } from "next";
import { Source_Serif_4, Source_Sans_3, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import LanguageWrapper from "@/components/LanguageWrapper";
import Navbar from "@/components/Navbar";

/**
 * Source Serif 4 — display font for headlines, page titles, pull quotes.
 * Chosen for literate, considered feel. Never Playfair, never Times.
 */
const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-source-serif",
  display: "swap",
});

/**
 * Source Sans 3 — UI font for body text, buttons, labels, form fields.
 * Chosen as a calmer, more literate alternative to Inter.
 */
const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-source-sans",
  display: "swap",
});

/**
 * IBM Plex Mono — used only for legal citations and case references
 * (e.g. "M.G.L. c.186 §15B"). Weight 400 only, no alternates.
 */
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CaseMate — Your legal friend",
  description:
    "CaseMate is a personalized legal assistant that knows your state, your situation, and explains your rights in plain English.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${sourceSerif.variable} ${sourceSans.variable} ${plexMono.variable}`}
    >
      <body className="bg-bg text-ink-primary font-sans antialiased">
        <ErrorBoundary>
          <AuthProvider>
            <Navbar />
            <LanguageWrapper>{children}</LanguageWrapper>
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
