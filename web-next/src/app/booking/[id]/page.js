"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
    CheckCircle2, Calendar, Clock, MapPin,
    ArrowRight, MessageSquare, ChevronLeft,
    Share2, User, Star
} from 'lucide-react';
import { getBooking } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function BookingDetailsPage() {
    const router = useRouter();
    const { id } = useParams();
    const [booking, setBooking] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetch = async () => {
            try {
                const res = await getBooking(id);
                setBooking(res.data);
            } catch (err) {
                console.error("Error fetching booking:", err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [id]);

    if (loading) return <div className="min-h-screen bg-black flex items-center justify-center"><LoadingSpinner /></div>;
    if (!booking) return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 text-center">
            <h2 className="text-xl font-black text-white mb-2">Booking Not Found</h2>
            <button onClick={() => router.push('/')} className="px-6 py-3 bg-zinc-900 rounded-2xl font-bold text-white cursor-pointer">Back to Home</button>
        </div>
    );

    return (
        <div className="flex flex-col min-h-screen bg-black text-white pb-32">
            <header className="p-4 pt-8 flex items-center justify-between">
                <button onClick={() => router.push('/')} className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer">
                    <ChevronLeft size={20} />
                </button>
                <h1 className="text-lg font-black tracking-tight">Booking Confirmed</h1>
                <button className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer">
                    <Share2 size={18} className="text-zinc-400" />
                </button>
            </header>

            <main className="flex-1 px-6 pt-10">
                <div className="flex flex-col items-center text-center mb-10">
                    <div className="w-20 h-20 bg-green-500/10 rounded-3xl flex items-center justify-center mb-6 border border-green-500/20 shadow-2xl shadow-green-500/10">
                        <CheckCircle2 size={40} className="text-green-500" />
                    </div>
                    <h2 className="text-3xl font-black mb-2 tracking-tight">You're all set!</h2>
                    <p className="text-zinc-500 font-medium">Your appointment is confirmed and synced.</p>
                </div>

                {/* Provider Card */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-[2.5rem] p-6 mb-8">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-16 h-16 bg-zinc-800 rounded-2xl flex items-center justify-center overflow-hidden border border-zinc-700">
                            {booking.provider_photo ? (
                                <img src={booking.provider_photo} className="w-full h-full object-cover" />
                            ) : (
                                <User size={32} className="text-zinc-600" />
                            )}
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-white">{booking.provider_name}</h3>
                            <div className="flex items-center text-amber-500 text-xs font-bold">
                                <Star size={12} fill="currentColor" className="mr-1" />
                                {booking.provider_rating || '5.0'} (24 reviews)
                            </div>
                        </div>
                        <div className="ml-auto">
                            <button
                                onClick={() => router.push(`/chat?role=consumer&initial=${encodeURIComponent(`I'd like to chat about my booking with ${booking.provider_name}`)}`)}
                                className="w-12 h-12 bg-white text-black rounded-full flex items-center justify-center shadow-xl hover:scale-110 transition-transform cursor-pointer"
                            >
                                <MessageSquare size={20} />
                            </button>
                        </div>
                    </div>

                    <div className="space-y-4 pt-6 border-t border-zinc-800/50">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center text-zinc-400">
                                <Calendar size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1">Date</p>
                                <p className="font-bold text-white text-sm">{booking.date}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center text-zinc-400">
                                <Clock size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1">Time</p>
                                <p className="font-bold text-white text-sm">{booking.time}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center text-zinc-400">
                                <MapPin size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest leading-none mb-1">Service Address</p>
                                <p className="font-bold text-white text-sm">Your Home Address</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-zinc-900/30 border border-dashed border-zinc-800 rounded-3xl p-6 text-center">
                    <p className="text-zinc-500 text-sm font-medium leading-relaxed">
                        Need to reschedule? Your agent can handle it for you. Just ask.
                    </p>
                    <button
                        onClick={() => router.push('/chat?role=consumer&initial=I need to reschedule my booking')}
                        className="mt-4 text-white text-sm font-black flex items-center justify-center mx-auto gap-1 cursor-pointer"
                    >
                        Talk to Agent <ArrowRight size={16} className="text-blue-500" />
                    </button>
                </div>
            </main>

            <div className="fixed bottom-0 left-0 right-0 p-5 bg-black/80 backdrop-blur-xl z-40">
                <div className="max-w-[480px] mx-auto">
                    <button
                        onClick={() => router.push('/')}
                        className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg shadow-2xl shadow-white/10 active:scale-95 transition-all cursor-pointer"
                    >
                        Return to Dashboard
                    </button>
                </div>
            </div>
        </div>
    );
}
