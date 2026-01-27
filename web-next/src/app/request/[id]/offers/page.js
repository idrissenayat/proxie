"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
    ChevronLeft, Star, MapPin, Clock, DollarSign,
    CheckCircle2, ArrowRight, Info, Filter, MessageSquare
} from 'lucide-react';
import { getRequest, getOffersForRequest, acceptOffer } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function OffersPage() {
    const router = useRouter();
    const { id: requestId } = useParams();
    const [request, setRequest] = useState(null);
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [acceptingId, setAcceptingId] = useState(null);

    useEffect(() => {
        const fetch = async () => {
            try {
                const [reqRes, offRes] = await Promise.all([
                    getRequest(requestId),
                    getOffersForRequest(requestId)
                ]);
                setRequest(reqRes.data);
                setOffers(offRes.data);
            } catch (err) {
                console.error("Error fetching offers:", err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [requestId]);

    const handleAccept = async (offerId) => {
        try {
            setAcceptingId(offerId);
            const res = await acceptOffer(offerId, {
                payment_method: "test_card",
                agreed_slots: [offers.find(o => o.id === offerId).available_slots[0]]
            });
            router.push(`/booking/${res.data.booking_id}`);
        } catch (err) {
            console.error("Error accepting offer:", err);
            alert("Failed to accept offer. Please try again.");
        } finally {
            setAcceptingId(null);
        }
    };

    if (loading) return <div className="min-h-screen bg-black flex items-center justify-center"><LoadingSpinner /></div>;

    return (
        <div className="flex flex-col min-h-screen bg-black text-white">
            <header className="fixed top-0 left-0 right-0 z-50 p-4 border-b border-zinc-800 bg-black/80 backdrop-blur-md">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <button onClick={() => router.back()} className="p-2 -ml-2 text-zinc-400 hover:text-white cursor-pointer">
                            <ChevronLeft size={24} />
                        </button>
                        <div>
                            <h1 className="text-xl font-black text-white">Offers ({offers.length})</h1>
                            <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">{request?.service_type}</p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 px-4 pt-24 pb-32 space-y-4">
                {offers.length === 0 ? (
                    <div className="text-center py-20 px-8">
                        <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-zinc-800">
                            <Clock size={32} className="text-zinc-600 animate-pulse" />
                        </div>
                        <h2 className="text-lg font-bold text-white mb-2">Finding the right pros...</h2>
                        <p className="text-zinc-500 text-sm leading-relaxed max-w-xs mx-auto">
                            Proxie is currently sharing your request with local specialists. You'll be notified as soon as offers arrive.
                        </p>
                    </div>
                ) : (
                    offers.map((offer) => (
                        <div key={offer.id} className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 hover:border-blue-500/30 transition-all group">
                            <div className="flex justify-between items-start mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 bg-zinc-800 rounded-xl flex items-center justify-center text-zinc-500 border border-zinc-700 overflow-hidden">
                                        {offer.provider_snapshot?.photo_url ? (
                                            <img src={offer.provider_snapshot.photo_url} alt="Pro" className="w-full h-full object-cover" />
                                        ) : (
                                            <User size={24} />
                                        )}
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-black text-white group-hover:text-blue-400 transition-colors">
                                            {offer.provider_snapshot?.name || 'Local Expert'}
                                        </h3>
                                        <div className="flex items-center text-amber-500 text-xs font-bold">
                                            <Star size={12} fill="currentColor" className="mr-1" />
                                            {offer.provider_snapshot?.rating || '5.0'} ({offer.provider_snapshot?.review_count || '24'})
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-1">Total Price</span>
                                    <span className="text-3xl font-black text-green-400">${offer.price}</span>
                                </div>
                            </div>

                            <p className="text-zinc-300 text-sm italic mb-6 leading-relaxed bg-black/30 p-4 rounded-2xl border border-zinc-800/50">
                                "{offer.message || 'I can help you with this! I have years of experience in this field and can get it done quickly.'}"
                            </p>

                            <div className="grid grid-cols-2 gap-3 mb-6">
                                <div className="flex items-center gap-2 text-xs text-zinc-400 font-medium">
                                    <Clock size={14} className="text-purple-400" />
                                    {offer.available_slots ? `${offer.available_slots[0].date} @ ${offer.available_slots[0].start_time}` : 'Available Soon'}
                                </div>
                                <div className="flex items-center gap-2 text-xs text-zinc-400 font-medium justify-end">
                                    <MapPin size={14} className="text-blue-400" />
                                    Match: {offer.distance || '2.4'} mi
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => router.push(`/chat?role=consumer&initial=${encodeURIComponent(`I have a question about ${offer.provider_snapshot?.name}'s offer`)}`)}
                                    className="flex-1 h-14 bg-zinc-800 border border-zinc-700 text-white rounded-2xl font-bold hover:bg-zinc-700 transition-all flex items-center justify-center gap-2 cursor-pointer"
                                >
                                    <MessageSquare size={18} /> Chat
                                </button>
                                <button
                                    onClick={() => handleAccept(offer.id)}
                                    disabled={acceptingId === offer.id}
                                    className="flex-[2] h-14 bg-white text-black rounded-2xl font-black hover:bg-zinc-200 transition-all shadow-xl shadow-white/5 disabled:opacity-50 cursor-pointer"
                                >
                                    {acceptingId === offer.id ? 'Processing...' : 'Accept Offer'}
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </main>
        </div>
    );
}
