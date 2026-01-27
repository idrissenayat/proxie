"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import {
    MapPin, Clock, DollarSign, MessageSquare,
    ArrowRight, Star, Calendar, CheckCircle2
} from 'lucide-react';

const RequestCard = ({ data, type }) => {
    const router = useRouter();

    const getStatusStyles = () => {
        switch (type) {
            case 'open': return 'text-amber-400';
            case 'pending': return 'text-blue-400';
            case 'upcoming': return 'text-purple-400';
            case 'completed': return 'text-green-400';
            default: return 'text-zinc-400';
        }
    };

    const renderCardContent = () => {
        if (type === 'upcoming') {
            return (
                <div className="space-y-3">
                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                            <span className="p-1.5 bg-purple-500/10 rounded-lg text-purple-400">
                                <Calendar size={16} />
                            </span>
                            <h3 className="text-white font-bold">{data.service_type}</h3>
                        </div>
                        <div className="text-right">
                            <p className="text-white font-bold text-sm">{data.scheduled_date}</p>
                            <p className="text-zinc-500 text-xs font-medium">{data.scheduled_time}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 py-2 border-y border-zinc-800/50">
                        <div className="w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center text-xs font-bold text-white">
                            {data.provider.name.charAt(0)}
                        </div>
                        <div>
                            <p className="text-zinc-300 text-sm font-medium">with {data.provider.name}</p>
                            <p className="text-zinc-500 text-[10px] flex items-center gap-1">
                                <Star size={10} className="fill-yellow-500 text-yellow-500" /> {data.provider.rating}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 text-zinc-500 text-xs">
                        <MapPin size={12} /> {data.location?.city}
                    </div>
                    <div className="flex gap-2 pt-1">
                        <button className="flex-1 bg-zinc-800 hover:bg-zinc-700 h-9 rounded-lg text-xs font-bold transition-colors cursor-pointer">
                            Message
                        </button>
                        <button
                            onClick={() => router.push(`/booking/${data.booking_id}`)}
                            className="flex-1 bg-white text-black h-9 rounded-lg text-xs font-bold transition-colors cursor-pointer"
                        >
                            Details
                        </button>
                    </div>
                </div>
            );
        }

        if (type === 'completed') {
            return (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="p-1.5 bg-green-500/10 rounded-lg text-green-400">
                            <CheckCircle2 size={16} />
                        </span>
                        <h3 className="text-white font-bold">{data.service_type}</h3>
                    </div>
                    <p className="text-zinc-500 text-xs font-medium">by {data.provider.name} • Completed Jan 20</p>

                    {!data.has_review && (
                        <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-3 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Star size={14} className="text-yellow-500" />
                                <span className="text-yellow-500/90 text-[11px] font-bold uppercase tracking-wider">Leave a review</span>
                            </div>
                            <button className="text-[11px] font-black text-white hover:underline cursor-pointer">REVIEW</button>
                        </div>
                    )}

                    {data.has_review && (
                        <div className="flex items-center gap-1">
                            {[...Array(5)].map((_, i) => (
                                <Star key={i} size={12} className={i < data.review_rating ? "fill-yellow-500 text-yellow-500" : "text-zinc-700"} />
                            ))}
                        </div>
                    )}

                    <div className="pt-1">
                        <button
                            onClick={() => router.push(`/chat?rebook=${data.booking_id}`)}
                            className="w-full bg-zinc-800 hover:bg-zinc-700 h-10 rounded-xl text-xs font-black uppercase tracking-widest transition-colors cursor-pointer"
                        >
                            Book Again
                        </button>
                    </div>
                </div>
            );
        }

        // Open or Pending
        return (
            <div className="space-y-4">
                <div
                    className="cursor-pointer group/content"
                    onClick={() => router.push(`/request/${data.id || data.booking_id}`)}
                >
                    <div className="flex justify-between items-start mb-1">
                        <h3 className="text-white font-bold text-base group-hover/content:text-blue-400 transition-colors">{data.title || data.service_type}</h3>
                        <ArrowRight size={14} className="text-zinc-700 group-hover/content:text-blue-400 group-hover/content:translate-x-1 transition-all" />
                    </div>
                    <div className="flex items-center gap-3 text-zinc-500 text-xs font-medium">
                        <span className="flex items-center gap-1"><MapPin size={12} /> {data.location?.city}</span>
                        <span className="flex items-center gap-1"><DollarSign size={12} /> {data.budget?.min}-{data.budget?.max}</span>
                    </div>
                </div>

                {type === 'open' ? (
                    <div className="flex items-center justify-between py-2 px-3 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                        <div className="flex items-center gap-2">
                            <Clock size={14} className="text-amber-400 animate-pulse" />
                            <span className="text-amber-400 text-xs font-bold uppercase tracking-wider">Waiting for offers</span>
                        </div>
                        <span className="text-zinc-600 text-[10px] font-medium">Posted 2h ago</span>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between py-2 px-3 bg-blue-500/5 border border-blue-500/10 rounded-xl">
                            <div className="flex items-center gap-2">
                                <MessageSquare size={14} className="text-blue-400" />
                                <span className="text-blue-400 text-xs font-bold uppercase tracking-wider">{data.offer_count} offers received</span>
                            </div>
                            <button
                                onClick={(e) => { e.stopPropagation(); router.push(`/offers?request_id=${data.id}`); }}
                                className="text-white text-[10px] font-black underline decoration-blue-500/50 underline-offset-4 cursor-pointer"
                            >
                                VIEW ALL
                            </button>
                        </div>
                        {data.best_offer && (
                            <div className="text-[11px] text-zinc-500 flex items-center gap-1.5 px-1 pb-1">
                                <span className="w-1 h-1 bg-zinc-700 rounded-full"></span>
                                Best: <span className="text-white font-bold">${data.best_offer.price}</span> by {data.best_offer.provider_name}
                                <Star size={10} className="fill-yellow-500 text-yellow-500 ml-0.5" /> {data.best_offer.provider_rating}
                            </div>
                        )}
                    </div>
                )}

                <div className="flex gap-2">
                    <button
                        onClick={(e) => { e.stopPropagation(); router.push(`/chat?request_id=${data.id}`); }}
                        className="flex-1 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 h-10 rounded-xl text-xs font-bold text-zinc-400 flex items-center justify-center gap-2 transition-all cursor-pointer"
                    >
                        <MessageSquare size={14} /> Ask Agent
                    </button>
                    {type === 'pending' && (
                        <button
                            onClick={(e) => { e.stopPropagation(); router.push(`/offers?request_id=${data.id}`); }}
                            className="flex-1 bg-white text-black h-10 rounded-xl text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1 shadow-lg shadow-white/5 cursor-pointer"
                        >
                            View Offers <ArrowRight size={14} />
                        </button>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="bg-zinc-900/40 border border-zinc-900 rounded-3xl p-5 hover:border-zinc-800 transition-all">
            {renderCardContent()}
        </div>
    );
};

export default RequestCard;
