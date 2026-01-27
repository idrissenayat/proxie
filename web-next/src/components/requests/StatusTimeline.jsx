"use client";

import React from 'react';
import { CheckCircle2, Clock, MessageSquare, XCircle, AlertCircle } from 'lucide-react';

const StatusTimeline = ({ history = [] }) => {
    if (!history || history.length === 0) return null;

    const getIcon = (status) => {
        switch (status) {
            case 'matching': return <Clock size={16} className="text-amber-400" />;
            case 'pending': return <MessageSquare size={16} className="text-blue-400" />;
            case 'upcoming': return <Clock size={16} className="text-purple-400" />;
            case 'completed': return <CheckCircle2 size={16} className="text-green-400" />;
            case 'cancelled': return <XCircle size={16} className="text-red-400" />;
            default: return <AlertCircle size={16} className="text-zinc-400" />;
        }
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="space-y-6">
            <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">Status Timeline</h3>
            <div className="relative">
                <div className="absolute left-[15px] top-2 bottom-2 w-px bg-zinc-800"></div>

                <div className="space-y-8">
                    {history.slice().reverse().map((event, i) => (
                        <div key={i} className="flex gap-4 relative">
                            <div className="z-10 w-8 h-8 rounded-full bg-black border border-zinc-800 flex items-center justify-center shrink-0">
                                {getIcon(event.status)}
                            </div>
                            <div className="pt-0.5">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-sm font-black text-white capitalize">{event.status}</span>
                                    <span className="text-[10px] font-bold text-zinc-600 uppercase tabular-nums">
                                        {formatDate(event.timestamp)}
                                    </span>
                                </div>
                                <p className="text-xs text-zinc-400 leading-relaxed font-medium">
                                    {event.note || `Status changed to ${event.status}`}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StatusTimeline;
