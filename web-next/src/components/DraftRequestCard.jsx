"use client";

import React from 'react';
import { MapPin, DollarSign, Clock, CheckCircle2 } from 'lucide-react';
import Button from './Button';

const DraftRequestCard = ({ data, onApprove, onEdit }) => {
    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-[2rem] p-6 w-full max-w-sm animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                    <CheckCircle2 className="text-blue-400" size={18} />
                </div>
                <h3 className="text-white font-black text-lg">Confirm Request</h3>
            </div>

            <div className="space-y-4 mb-6">
                <div>
                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1 block">Service</label>
                    <p className="text-white font-bold">{data.service_type}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1 block">Budget</label>
                        <div className="flex items-center text-zinc-300 font-bold">
                            <DollarSign size={14} className="mr-0.5" />
                            {data.budget?.min}-{data.budget?.max}
                        </div>
                    </div>
                    <div>
                        <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1 block">Location</label>
                        <div className="flex items-center text-zinc-300 font-bold">
                            <MapPin size={14} className="mr-0.5" />
                            {data.location?.city || 'Local'}
                        </div>
                    </div>
                </div>

                <div>
                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1 block">Description</label>
                    <p className="text-zinc-400 text-sm italic">"{data.raw_input}"</p>
                </div>
            </div>

            <div className="flex flex-col gap-2">
                <Button title="Post Request" onClick={onApprove} />
                <button
                    onClick={onEdit}
                    className="w-full py-3 text-zinc-500 text-xs font-bold uppercase tracking-widest hover:text-white transition-colors cursor-pointer"
                >
                    Edit Details
                </button>
            </div>
        </div>
    );
};

export default DraftRequestCard;
