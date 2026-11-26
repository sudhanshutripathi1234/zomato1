import type { Metadata } from "next";
import { Karla, Playfair_Display } from "next/font/google";
import { FoodBackdrop } from "@/components/FoodBackdrop";
import "./globals.css";

const playfair = Playfair_Display({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const karla = Karla({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SPICE AI",
  description:
    "Filter real Zomato listings, then let AI rank and explain the best fits.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${playfair.variable} ${karla.variable} min-h-screen font-sans text-white antialiased`}
      >
        <FoodBackdrop />
        <div className="app-shell">{children}</div>
      </body>
    </html>
  );
}
