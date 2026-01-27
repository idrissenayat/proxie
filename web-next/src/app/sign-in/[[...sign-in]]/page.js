"use client";

import { SignIn } from "@clerk/nextjs";
import Link from "next/link";
import { ChevronLeft, Sparkles } from "lucide-react";

export default function SignInPage() {
    return (
        <div className="flex flex-col min-h-screen bg-black text-white p-6 relative overflow-hidden">
            {/* Background elements for premium feel */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[300px] h-[300px] bg-blue-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[300px] h-[300px] bg-purple-600/10 blur-[120px] rounded-full" />
            </div>

            <nav className="relative z-10 flex items-center justify-between mb-12">
                <Link href="/" className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 hover:bg-zinc-800 transition-colors">
                    <ChevronLeft size={18} className="text-zinc-400" />
                </Link>
                <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-black text-sm">P</span>
                    </div>
                    <span className="font-black tracking-tight">Proxie</span>
                </div>
                <div className="w-10" /> {/* Spacer */}
            </nav>

            <div className="relative z-10 flex-1 flex flex-col items-center justify-center max-w-sm mx-auto w-full">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center space-x-2 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full mb-4">
                        <Sparkles size={12} className="text-blue-400" />
                        <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Connect your agent</span>
                    </div>
                    <h1 className="text-4xl font-black mb-3 tracking-tight">Welcome Back</h1>
                    <p className="text-zinc-500 text-sm">Pick up where you left off with your personal concierge.</p>
                </div>

                <div className="w-full clerk-theme-wrapper">
                    <SignIn
                        appearance={{
                            elements: {
                                rootBox: "w-full",
                                card: "bg-transparent shadow-none border-none p-0",
                                headerTitle: "hidden",
                                headerSubtitle: "hidden",
                                socialButtonsBlockButton: "bg-zinc-900 border-zinc-800 hover:bg-zinc-800 text-white font-bold h-12 rounded-xl transition-all",
                                socialButtonsProviderIcon: "filter brightness-200",
                                dividerRow: "text-zinc-700",
                                dividerLine: "bg-zinc-900",
                                formFieldLabel: "text-zinc-500 text-xs font-bold uppercase tracking-widest mb-2",
                                formFieldInput: "bg-zinc-900 border-zinc-800 text-white rounded-xl h-12 focus:border-blue-500 focus:ring-0 transition-all",
                                formButtonPrimary: "bg-white text-black hover:bg-zinc-200 font-black h-12 rounded-xl transition-all text-sm uppercase tracking-tight shadow-xl shadow-white/5",
                                footerAction: "text-zinc-500",
                                footerActionLink: "text-blue-400 hover:text-blue-300 font-bold",
                                identityPreviewText: "text-white",
                                identityPreviewEditButtonIcon: "text-zinc-500",
                                formResendCodeLink: "text-blue-400",
                                otpCodeFieldInput: "bg-zinc-900 border-zinc-800 text-white rounded-xl h-14"
                            }
                        }}
                    />
                </div>
            </div>

            <footer className="relative z-10 text-center py-8">
                <p className="text-zinc-600 text-xs">
                    By continuing, you agree to Proxie's <span className="underline">Terms</span> and <span className="underline">Privacy</span>.
                </p>
            </footer>

            <style jsx global>{`
                .clerk-theme-wrapper .cl-internal-1dauvpw { display: none; }
                .clerk-theme-wrapper .cl-internal-phv686 { display: none; }
            `}</style>
        </div>
    );
}
