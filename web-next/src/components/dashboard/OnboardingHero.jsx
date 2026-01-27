import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck, Zap, Heart } from 'lucide-react';
import Link from 'next/link';

const OnboardingHero = ({ onStartChat }) => {
    return (
        <div className="py-12 px-6 text-center animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full mb-8 shadow-xl">
                <Sparkles size={12} className="text-blue-400" />
                <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Powered by Gemini Pro</span>
            </div>

            <h1 className="text-5xl font-black text-white mb-6 tracking-tight leading-[1.1]">
                Your Personal <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">Service Concierge</span>
            </h1>

            <p className="text-zinc-500 text-lg mb-10 max-w-[300px] mx-auto leading-relaxed">
                Finding the right professional shouldn't be a chore. Chat with Proxie to get anything done.
            </p>

            <button
                onClick={onStartChat}
                className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg flex items-center justify-center space-x-3 shadow-2xl shadow-white/10 hover:scale-[1.02] active:scale-95 transition-all cursor-pointer"
            >
                <span>Start a Request</span>
                <ArrowRight size={20} />
            </button>

            <div className="grid grid-cols-2 gap-4 mt-12">
                <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-2xl text-left hover:border-zinc-700 transition-colors">
                    <Zap size={20} className="text-amber-400 mb-2" />
                    <h3 className="text-white font-bold text-sm">Instant Drafts</h3>
                    <p className="text-zinc-500 text-[11px] mt-1 leading-snug">AI understands your needs and drafts the perfect request.</p>
                </div>
                <div className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-2xl text-left hover:border-zinc-700 transition-colors">
                    <ShieldCheck size={20} className="text-emerald-400 mb-2" />
                    <h3 className="text-white font-bold text-sm">Verified Pros</h3>
                    <p className="text-zinc-500 text-[11px] mt-1 leading-snug">We only match you with specialists who've passed our bar.</p>
                </div>
            </div>

            <div className="mt-12 pt-12 border-t border-zinc-900">
                <p className="text-xs text-zinc-600 font-bold uppercase tracking-widest mb-6 italic">Trusted by specialists in</p>
                <div className="flex justify-center flex-wrap gap-4 opacity-50 grayscale">
                    <span className="text-sm font-black text-white tracking-tighter">HAIR & BEAUTY</span>
                    <span className="text-sm font-black text-white tracking-tighter">HOME REPAIR</span>
                    <span className="text-sm font-black text-white tracking-tighter">CREATIVE</span>
                </div>
            </div>
        </div>
    );
};

export default OnboardingHero;
