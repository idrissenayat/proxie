"use client";

import React from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

const MediaViewer = ({ isOpen, media, index, onClose, onPrev, onNext }) => {
    if (!isOpen || !media || media.length === 0) return null;

    const currentMedia = media[index];

    return (
        <div className="fixed inset-0 z-[100] bg-black flex flex-col">
            <header className="p-4 flex items-center justify-between z-10">
                <span className="text-white font-bold text-sm">
                    {index + 1} / {media.length}
                </span>
                <button
                    onClick={onClose}
                    className="p-2 bg-zinc-800 rounded-full text-white hover:bg-zinc-700 cursor-pointer"
                >
                    <X size={24} />
                </button>
            </header>

            <div className="flex-1 relative flex items-center justify-center p-4">
                {currentMedia.type === 'video' ? (
                    <video
                        src={currentMedia.preview || currentMedia.url}
                        controls
                        autoPlay
                        className="max-w-full max-h-full object-contain"
                    />
                ) : (
                    <img
                        src={currentMedia.preview || currentMedia.url}
                        alt="Media"
                        className="max-w-full max-h-full object-contain"
                    />
                )}

                {media.length > 1 && (
                    <>
                        <button
                            onClick={onPrev}
                            className="absolute left-4 p-4 bg-black/50 rounded-full text-white hover:bg-black/80 cursor-pointer"
                        >
                            <ChevronLeft size={32} />
                        </button>
                        <button
                            onClick={onNext}
                            className="absolute right-4 p-4 bg-black/50 rounded-full text-white hover:bg-black/80 cursor-pointer"
                        >
                            <ChevronRight size={32} />
                        </button>
                    </>
                )}
            </div>

            <footer className="p-6 bg-gradient-to-t from-black to-transparent">
                <p className="text-zinc-400 text-xs text-center">
                    Tap anywhere to close
                </p>
            </footer>
        </div>
    );
};

export default MediaViewer;
