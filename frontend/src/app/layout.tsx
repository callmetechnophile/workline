import { ClerkProvider } from "@clerk/nextjs";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://worklineai.netlify.app"),
  title: "Workline AI - Hardware Engineering Workflow Planner",
  description: "Automated hardware engineering workflow planner, autonomous multi-agent research, and verified BOM optimization.",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/icon.png",
    apple: "/icon.png",
  },
  openGraph: {
    title: "Workline AI",
    description: "Automated hardware engineering workflow planner",
    siteName: "Workline AI",
    images: [{ url: "/icon.png" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Workline AI",
    description: "Automated hardware engineering workflow planner",
    images: ["/icon.png"],
  },
  verification: {
    other: {
      "strix-verification": "strix-verify-bb442cfb256a19c1620df82777eac719",
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const publishableKey =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
    "pk_test_bW9yYWwtcHVwLTkxLmNsZXJrLmFjY291bnRzLmRldiQ";

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <ClerkProvider publishableKey={publishableKey}>
          {children}
        </ClerkProvider>
      </body>
    </html>
  );
}