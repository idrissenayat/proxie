"use client";

import React, { useState } from 'react';
import { Plus, Trash2, Camera, X } from 'lucide-react';

const PortfolioManager = ({ photos = [], onAdd, onDelete }) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newPhotoUrl, setNewPhotoUrl] = useState('');
    const [caption, setCaption] = useState('');

    const handleAdd = () => {
        if (!newPhotoUrl) return;
        onAdd({ photo_url: newPhotoUrl, caption: caption });
        setNewPhotoUrl('');
        setCaption('');
        setIsAdding(false);
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Portfolio Management</h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="w-8 h-8 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center text-white cursor-pointer"
                >
                    {isAdding ? <X size={16} /> : <Plus size={16} />}
                </button>
            </div>

            {isAdding && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-5 space-y-4 animate-in slide-in-from-top-2 duration-300">
                    <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                        <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Image URL</span>
                        <input
                            className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                            value={newPhotoUrl}
                            onChange={(e) => setNewPhotoUrl(e.target.value)}
                            placeholder="https://example.com/photo.jpg"
                        />
                    </div>
                    <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                        <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Caption</span>
                        <input
                            className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                            value={caption}
                            onChange={(e) => setCaption(e.target.value)}
                            placeholder="Project description..."
                        />
                    </div>
                    <button
                        onClick={handleAdd}
                        className="w-full h-12 bg-white text-black rounded-xl font-black text-sm cursor-pointer"
                    >
                        Add to Portfolio
                    </button>
                </div>
            )}

            <div className="grid grid-cols-2 gap-3">
                {photos.map((photo) => (
                    <div key={photo.id} className="relative rounded-2xl overflow-hidden aspect-square group">
                        <img src={photo.photo_url} alt={photo.caption} className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center gap-2">
                            <button
                                onClick={() => onDelete(photo.id)}
                                className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center text-white cursor-pointer"
                            >
                                <Trash2 size={18} />
                            </button>
                        </div>
                    </div>
                ))}
                {photos.length === 0 && !isAdding && (
                    <div className="col-span-2 py-12 border-2 border-dashed border-zinc-800 rounded-3xl flex flex-col items-center justify-center text-zinc-600">
                        <Camera size={32} className="mb-2 opacity-20" />
                        <p className="text-sm font-bold">No portfolio photos yet</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PortfolioManager;
