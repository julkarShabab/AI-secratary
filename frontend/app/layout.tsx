import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { ChatProvider } from "@/contexts/ChatContext";
import { ThemeProvider } from "@/components/theme-provider";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Aria — AI Secretary",
  description: "Your always-on AI secretary",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable} h-screen antialiased overflow-hidden`}
      suppressHydrationWarning
    >
      <body className="h-screen flex flex-col overflow-hidden">
        <ThemeProvider>
          <AuthProvider>
            <ChatProvider>{children}</ChatProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}