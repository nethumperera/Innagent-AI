import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "InnAgent AI — Hotel Management Dashboard",
  description:
    "Multi-agent AI hotel management platform for Co Host Ceylon. Manages pricing, guest communication, revenue analytics, reviews, and operations for boutique hotels in Sri Lanka.",
  keywords: ["hotel management", "AI", "Sri Lanka", "Co Host Ceylon", "InnAgent AI"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased bg-background text-foreground dark:bg-gray-950 dark:text-white">
        {children}
      </body>
    </html>
  );
}
