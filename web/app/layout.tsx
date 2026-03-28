import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CaseMate — AI Legal Assistant",
  description:
    "Your personal AI legal assistant. Get personalized legal guidance with memory, state-specific citations, and actionable documents.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#050505] text-white`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
