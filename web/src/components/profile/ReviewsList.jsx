import React from 'react';
import { Star, User } from 'lucide-react';

const ReviewsList = ({ reviews = [] }) => {
    if (!reviews || reviews.length === 0) {
        return (
            <div className="bg-zinc-900/40 border border-zinc-900 rounded-3xl p-8 text-center">
                <p className="text-zinc-500 font-medium">No reviews yet. Be the first to book!</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">Reviews ({reviews.length})</h3>
            <div className="space-y-4">
                {reviews.map((review, i) => (
                    <div key={i} className="bg-zinc-900/40 border border-zinc-900 rounded-3xl p-5 space-y-3">
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center text-zinc-500">
                                    <User size={16} />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-white">{review.author_name || 'Anonymous'}</p>
                                    <p className="text-[10px] text-zinc-600 font-bold uppercase tracking-wider">{review.date}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-1">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} size={12} className={i < review.rating ? "fill-yellow-500 text-yellow-500" : "text-zinc-700"} />
                                ))}
                            </div>
                        </div>
                        <p className="text-sm text-zinc-400 leading-relaxed italic">"{review.comment}"</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReviewsList;
