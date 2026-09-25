import type { Metadata } from "next";
import { GuildThemeProvider } from "@/lib/guilds/GuildThemeProvider";
import "./globals.css";

// NOTE: this sandbox can't reach fonts.googleapis.com, so font loading
// is stubbed out here. On your machine, swap this back to:
//
//   import { Bebas_Neue, Inter } from "next/font/google";
//
//   const inter = Inter({ variable: "--font-inter", subsets: ["latin"], weight: ["400", "500"] });
//   const bebasNeue = Bebas_Neue({ variable: "--font-bebas", subsets: ["latin"], weight: ["400"] });
//
// and add `${inter.variable} ${bebasNeue.variable}` back to the <html> className.
// This will work fine once you're running locally with normal internet access.

export const metadata: Metadata = {
  title: "Deck Finder — UK Magic: The Gathering price optimiser",
  description:
    "Paste your deck list and find the cheapest combination of UK vendors.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <GuildThemeProvider>{children}</GuildThemeProvider>
      </body>
    </html>
  );
}
