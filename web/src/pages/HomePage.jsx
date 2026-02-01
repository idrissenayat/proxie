import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Briefcase, MessageSquare, ArrowRight } from 'lucide-react';

const HomePage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-96 bg-blue-600/10 blur-[100px] rounded-full -translate-y-1/2 pointer-events-none" />
            <div className="absolute bottom-0 right-0 w-full h-96 bg-purple-600/10 blur-[100px] rounded-full translate-y-1/2 pointer-events-none" />

            {/* Header */}
            <div className="text-center mb-12 z-10 animate-in fade-in slide-in-from-top-8 duration-700">
                <h1 className="text-6xl font-black tracking-tighter mb-2 bg-gradient-to-br from-white via-zinc-200 to-zinc-500 bg-clip-text text-transparent">
                    Proxie
                </h1>
                <p className="text-zinc-500 font-medium text-lg tracking-wide">
                    Your craft, represented
                </p>
            </div>

            {/* Main Cards Container */}
            <div className="w-full max-w-md space-y-6 z-10">

                {/* 1. Consumer Card */}
                <div className="group relative bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-[2rem] p-8 overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:border-zinc-700 hover:shadow-2xl hover:shadow-blue-500/10">
                    <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                        <Search size={64} className="text-white" />
                    </div>

                    <div className="relative">
                        <h2 className="text-3xl font-bold mb-2">Find a Service</h2>
                        <p className="text-zinc-400 mb-8 max-w-[200px] leading-relaxed">
                            Find vetted professionals for any task, instantly.
                        </p>

                        <button
                            onClick={() => navigate('/chat?role=consumer')}
                            className="w-full h-14 bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl font-bold text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 active:scale-[0.98] transition-all flex items-center justify-center gap-2 group-hover:translate-x-1 duration-300"
                        >
                            <MessageSquare size={20} className="fill-current" />
                            Chat with Agent
                        </button>
                    </div>
                </div>

                {/* 2. Provider Card */}
                <div className="group relative bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-[2rem] p-8 overflow-hidden transition-all duration-300 hover:scale-[1.02] hover:border-zinc-700 hover:shadow-2xl hover:shadow-green-500/10">
                    <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                        <Briefcase size={64} className="text-emerald-400" />
                    </div>

                    <div className="relative">
                        <h2 className="text-3xl font-bold mb-2 text-white">Earn as a Pro</h2>
                        <p className="text-zinc-400 mb-8 max-w-[200px] leading-relaxed">
                            Join skilled providers and get matched with leads.
                        </p>

                        <div className="flex gap-3">
                            <button
                                onClick={() => navigate('/chat?role=enrollment&initial=I want to join Proxie')}
                                className="flex-1 h-14 bg-white text-black rounded-xl font-bold shadow-lg shadow-white/5 hover:bg-zinc-200 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
                            >
                                Start Enrollment
                            </button>
                            <button
                                onClick={() => navigate('/provider')}
                                className="w-14 h-14 bg-zinc-800 rounded-xl flex items-center justify-center hover:bg-zinc-700 active:scale-95 transition-all border border-zinc-700"
                                title="Provider Dashboard"
                            >
                                <ArrowRight size={20} />
                            </button>
                        </div>
                    </div>
                </div>

            </div>

            {/* Footer */}
            <footer className="mt-16 text-zinc-600 text-sm font-medium">
                © 2026 Proxie Platform
            </footer>
        </div>
    );
};

export default HomePage;
