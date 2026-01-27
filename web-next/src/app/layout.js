import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider, SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Proxie | Your Craft, Represented",
  description: "AI-powered agent for finding and managing local services.",
};

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="bg-black antialiased text-white">
          <div className="max-w-[480px] mx-auto flex flex-col min-h-screen border-x border-zinc-900 shadow-2xl">
            {children}
          </div>
        </body>
      </html>
    </ClerkProvider>
  );
}
