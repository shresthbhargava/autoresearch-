import type { Metadata } from "next";
import { Inter, Space_Grotesk, Space_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-grotesk",
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

const spaceMono = Space_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AutoResearch AI - BRD Generator",
  description:
    "Enterprise multi-agent Business Requirement Document (BRD) generation tool powered by Gemini 2.5 Pro.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`
        ${spaceGrotesk.variable}
        ${spaceMono.variable}
        ${inter.variable}
        dark selection:bg-accent/30 selection:text-accent
      `}
    >
      <body className="font-grotesk bg-background text-foreground min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
