"use client";

import React from 'react';
import { Camera } from 'lucide-react';

const MediaGallery = ({ media = [], onOpenViewer }) => {
    if (!media || media.length === 0) {
        return (
            <div className="w-full aspect-video bg-zinc-900 rounded-3xl flex flex-col items-center justify-center text-zinc-700 border border-zinc-800">
                <Camera size={48} className="mb-3 opacity-20" />
                <span className="text-xs font-bold uppercase tracking-widest opacity-30">No Media Provided</span>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
                {media.slice(0, 4).map((item, index) => (
                    <div
                        key={index}
                        onClick={() => onOpenViewer(index)}
                        className={`relative rounded-3xl overflow-hidden cursor-pointer group ${index === 0 && media.length === 1 ? 'col-span-2 aspect-video' :
                            index === 0 && media.length > 2 ? 'row-span-2 aspect-auto' : 'aspect-square'
                            }`}
                    >
                        <img
                            src={item.url || item.preview}
                            alt={`Media ${index}`}
                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all"></div>

                        {index === 3 && media.length > 4 && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center">
                                <span className="text-xl font-black text-white">+{media.length - 4}</span>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MediaGallery;
