"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
    User, MapPin, Star, Shield,
    ChevronLeft, Edit3, Settings, LogOut,
    CheckCircle2, Plus, X, Camera
} from 'lucide-react';
import { getProviders } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function ProviderProfilePage() {
    const router = useRouter();
    const [provider, setProvider] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetch = async () => {
            try {
                const res = await getProviders();
                // For demo, just pick the first one or if we had a stored ID
                setProvider(res.data[0]);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, []);

    if (loading) return <div className="min-h-screen bg-black flex items-center justify-center"><LoadingSpinner /></div>;
    if (!provider) return <div className="min-h-screen bg-black p-8 text-center text-zinc-500">Profile not found</div>;

    return (
        <div className="flex flex-col min-h-screen bg-black text-white">
            <header className="p-4 pt-8 flex items-center justify-between">
                <button onClick={() => router.back()} className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-lg font-black tracking-tight">Business Profile</h1>
                <button className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer">
                    <Settings size={18} className="text-zinc-400" />
                </button>
            </header>

            <main className="flex-1 px-6 pt-6 pb-32">
                {/* Profile Hero */}
                <div className="flex flex-col items-center text-center mb-10">
                    <div className="relative mb-4">
                        <div className="w-32 h-32 bg-zinc-900 rounded-[2.5rem] border-4 border-zinc-800 flex items-center justify-center overflow-hidden">
                            {provider.photo_url ? (
                                <img src={provider.photo_url} alt="Profile" className="w-full h-full object-cover" />
                            ) : (
                                <User size={48} className="text-zinc-700" />
                            )}
                        </div>
                        <button className="absolute bottom-1 right-1 w-10 h-10 bg-blue-600 rounded-full border-4 border-black flex items-center justify-center text-white cursor-pointer">
                            <Camera size={16} />
                        </button>
                    </div>
                    <h2 className="text-3xl font-black mb-1">{provider.name}</h2>
                    <div className="flex items-center gap-2 mb-4">
                        <div className="flex items-center text-amber-500 font-bold text-sm bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
                            <Star size={14} fill="currentColor" className="mr-1" />
                            {provider.rating || '5.0'}
                        </div>
                        <div className="flex items-center text-blue-400 font-bold text-sm bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
                            <Shield size={14} className="mr-1" /> Verified
                        </div>
                    </div>
                    <p className="text-zinc-500 text-sm max-w-xs leading-relaxed">
                        {provider.bio || "Professional craftsman providing high-quality services in your local area."}
                    </p>
                </div>

                {/* Services Section */}
                <section className="mb-10">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xs font-black text-zinc-500 uppercase tracking-widest">Active Services</h3>
                        <button className="text-blue-500 text-xs font-bold cursor-pointer">Manage</button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        {provider.specializations?.map((spec, i) => (
                            <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
                                <span className="bg-blue-500/20 text-blue-400 text-[10px] font-black px-2 py-0.5 rounded uppercase mb-2 inline-block">Pro</span>
                                <p className="font-bold text-white text-sm">{spec}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Verification Section */}
                <section className="bg-zinc-900/50 border border-zinc-900 rounded-3xl p-6 mb-10">
                    <h3 className="text-sm font-black mb-4">Verification Check</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                                    <CheckCircle2 size={16} className="text-green-500" />
                                </div>
                                <span className="text-sm font-medium text-zinc-300">Identity Verified</span>
                            </div>
                            <span className="text-[10px] font-bold text-zinc-500 italic">2026-01-20</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                                    <CheckCircle2 size={16} className="text-green-500" />
                                </div>
                                <span className="text-sm font-medium text-zinc-300">Liability Insurance</span>
                            </div>
                            <span className="text-[10px] font-bold text-zinc-500 italic">Valid</span>
                        </div>
                    </div>
                </section>

                {/* Logout */}
                <button className="w-full h-14 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center justify-center gap-3 text-red-500 font-bold hover:bg-red-500/20 transition-all cursor-pointer">
                    <LogOut size={18} /> Log Out Business
                </button>
            </main>
        </div>
    );
}
