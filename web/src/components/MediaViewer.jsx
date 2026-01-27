import React from 'react';
import { X, ChevronLeft, ChevronRight, Download } from 'lucide-react';

const MediaViewer = ({ media, currentIndex, onClose, onNavigate }) => {
    if (!media || media.length === 0) return null;

    const currentMedia = media[currentIndex];

    return (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex flex-col items-center justify-center animate-in fade-in duration-200">
            {/* Top Bar */}
            <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent">
                <div className="text-white text-sm font-bold">
                    {currentIndex + 1} / {media.length}
                </div>
                <div className="flex items-center gap-4">
                    <a
                        href={currentMedia.preview || currentMedia.url}
                        download={`proxie-media-${currentMedia.id}`}
                        className="p-2 text-zinc-400 hover:text-white transition-colors"
                    >
                        <Download size={20} />
                    </a>
                    <button
                        onClick={onClose}
                        className="p-2 text-zinc-400 hover:text-white transition-colors bg-white/10 rounded-full"
                    >
                        <X size={20} />
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="w-full h-full flex items-center justify-center relative touch-none">
                {media.length > 1 && (
                    <>
                        <button
                            onClick={(e) => { e.stopPropagation(); onNavigate((currentIndex - 1 + media.length) % media.length); }}
                            className="absolute left-4 p-4 text-white/50 hover:text-white transition-colors bg-white/5 hover:bg-white/10 rounded-full"
                        >
                            <ChevronLeft size={32} />
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); onNavigate((currentIndex + 1) % media.length); }}
                            className="absolute right-4 p-4 text-white/50 hover:text-white transition-colors bg-white/5 hover:bg-white/10 rounded-full"
                        >
                            <ChevronRight size={32} />
                        </button>
                    </>
                )}

                <div className="max-w-4xl max-h-[85vh] w-full p-4 flex items-center justify-center">
                    {currentMedia.type === 'image' ? (
                        <img
                            src={currentMedia.preview || currentMedia.url}
                            alt="View"
                            className="max-w-full max-h-full object-contain shadow-2xl rounded-lg animate-in zoom-in-95 duration-300"
                        />
                    ) : (
                        <video
                            src={currentMedia.preview || currentMedia.url}
                            controls
                            autoPlay
                            className="max-w-full max-h-full rounded-lg shadow-2xl"
                        />
                    )}
                </div>
            </div>

            {/* Thumbnail Strip */}
            {media.length > 1 && (
                <div className="absolute bottom-8 left-0 right-0 p-4 flex justify-center gap-2 overflow-x-auto">
                    {media.map((item, idx) => (
                        <button
                            key={idx}
                            onClick={() => onNavigate(idx)}
                            className={`w-12 h-12 rounded-md overflow-hidden border-2 transition-all ${idx === currentIndex ? 'border-blue-500 scale-110 shadow-lg' : 'border-zinc-800 opacity-50 hover:opacity-100'
                                }`}
                        >
                            <img src={item.preview || item.url} alt="Thumb" className="w-full h-full object-cover" />
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MediaViewer;
