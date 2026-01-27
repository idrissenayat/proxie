"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronLeft } from 'lucide-react';
import { UserButton, SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';

const Header = ({ title, showBack = false }) => {
    const router = useRouter();

    return (
        <header className="flex items-center justify-between p-4 sticky top-0 bg-black/80 backdrop-blur-md z-10 border-b border-zinc-900">
            <div className="flex items-center space-x-2">
                {showBack && (
                    <button onClick={() => router.back()} className="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors cursor-pointer">
                        <ChevronLeft size={24} />
                    </button>
                )}
                {!showBack && (
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <span className="text-white font-black text-sm">P</span>
                        </div>
                        <h1 className="text-lg font-black text-white tracking-tight italic">{title || "Proxie"}</h1>
                    </div>
                )}
                {showBack && <h1 className="text-lg font-black text-white tracking-tight italic">{title}</h1>}
            </div>

            <div className="flex items-center space-x-3">
                <SignedIn>
                    <UserButton
                        appearance={{
                            elements: {
                                userButtonAvatarBox: "w-9 h-9 border border-zinc-800",
                                userButtonPopoverCard: "bg-zinc-900 border border-zinc-800 text-white",
                                userButtonPopoverActionButton: "hover:bg-zinc-800",
                                userButtonPopoverActionButtonText: "text-zinc-300",
                                userButtonPopoverFooter: "hidden"
                            }
                        }}
                    />
                </SignedIn>
                <SignedOut>
                    <Link href="/sign-in" className="text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-white transition-colors cursor-pointer px-4 py-2 bg-zinc-900 rounded-full border border-zinc-800">
                        Sign In
                    </Link>
                </SignedOut>
            </div>
        </header>
    );
};

export default Header;
