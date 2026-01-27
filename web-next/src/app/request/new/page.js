"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, Sparkles, Send, AudioWaveform } from 'lucide-react';

export default function CreateRequestPage() {
    const router = useRouter();
    const [input, setInput] = useState('');

    const handleSubmit = () => {
        if (!input.trim()) return;
        router.push(`/chat?role=consumer&initial=${encodeURIComponent(input)}`);
    };

    return (
        <div className="flex flex-col min-h-screen bg-black text-white">
            <header className="p-4 pt-8 flex items-center justify-between">
                <button onClick={() => router.back()} className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-lg font-black tracking-tight">New Request</h1>
                <div className="w-10" />
            </header>

            <main className="flex-1 px-6 pt-10">
                <div className="mb-10">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center mb-6 border border-blue-500/20">
                        <Sparkles size={24} className="text-blue-400" />
                    </div>
                    <h2 className="text-4xl font-black mb-4 tracking-tight leading-tight italic">
                        Tell Proxie what you need.
                    </h2>
                    <p className="text-zinc-500 font-medium text-lg leading-relaxed">
                        Speak naturally. "I need a haircut Friday at 2pm" or "My sink is leaking and I need someone ASAP."
                    </p>
                </div>

                <div className="relative">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type anything..."
                        className="w-full bg-zinc-900/50 border-2 border-zinc-800 rounded-[2.5rem] p-8 h-64 text-xl font-medium placeholder-zinc-700 outline-none focus:border-blue-500/50 transition-all resize-none"
                    />
                    <div className="absolute bottom-6 right-6 flex items-center gap-3">
                        <button className="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center text-zinc-500 hover:text-white transition-colors cursor-pointer">
                            <AudioWaveform size={20} />
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={!input.trim()}
                            className="w-12 h-12 bg-white text-black rounded-full flex items-center justify-center shadow-xl hover:scale-110 active:scale-95 transition-all disabled:opacity-50 cursor-pointer"
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>

                <div className="mt-10 grid grid-cols-1 gap-3">
                    <div className="bg-zinc-900/40 border border-zinc-900 rounded-2xl p-4 flex items-center justify-between group hover:bg-zinc-900 transition-colors cursor-pointer" onClick={() => setInput("I need my house cleaned this weekend")}>
                        <span className="text-zinc-400 font-medium">✨ "I need my house cleaned this weekend"</span>
                    </div>
                    <div className="bg-zinc-900/40 border border-zinc-900 rounded-2xl p-4 flex items-center justify-between group hover:bg-zinc-900 transition-colors cursor-pointer" onClick={() => setInput("Plumber for a leaky faucet")}>
                        <span className="text-zinc-400 font-medium">✨ "Plumber for a leaky faucet"</span>
                    </div>
                </div>
            </main>
        </div>
    );
}
