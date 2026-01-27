import React from 'react';
import RequestCard from './RequestCard';

const RequestSection = ({ title, icon: Icon, requests, type, onViewAll }) => {
    if (!requests || requests.length === 0) return null;

    return (
        <section className="space-y-4">
            <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                    {Icon && <Icon size={18} className={
                        type === 'open' ? 'text-amber-400' :
                            type === 'pending' ? 'text-blue-400' :
                                type === 'upcoming' ? 'text-purple-400' :
                                    'text-green-400'
                    } />}
                    <h2 className="text-sm font-black uppercase tracking-[0.15em] text-zinc-400">
                        {title} {requests.length > 0 && `(${requests.length})`}
                    </h2>
                </div>
                {onViewAll && (
                    <button
                        onClick={onViewAll}
                        className="text-[10px] font-black text-zinc-500 hover:text-white uppercase tracking-wider transition-colors"
                    >
                        View All
                    </button>
                )}
            </div>
            <div className="space-y-3">
                {requests.map((req, i) => (
                    <RequestCard key={req.id || req.booking_id} data={req} type={type} />
                ))}
            </div>
        </section>
    );
};

export default RequestSection;
