import React, { useRef } from 'react';
import { Camera, Image as ImageIcon, Plus, X } from 'lucide-react';

const PortfolioUploader = ({ photos = [], onAdd, onRemove }) => {
    const fileRef = useRef(null);

    const handleFile = (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (event) => {
                onAdd({
                    id: Date.now() + Math.random(),
                    file,
                    preview: event.target.result,
                    name: file.name
                });
            };
            reader.readAsDataURL(file);
        });
    };

    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-[2rem] p-6 w-full max-w-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-white font-black text-lg mb-4 flex items-center">
                <Camera className="mr-2 text-zinc-500" size={20} />
                Show your work
            </h3>

            <div className="grid grid-cols-3 gap-3 mb-6">
                {photos.map((photo) => (
                    <div key={photo.id} className="relative aspect-square">
                        <img
                            src={photo.preview}
                            alt=""
                            className="w-full h-full object-cover rounded-xl border border-zinc-700"
                        />
                        <button
                            onClick={() => onRemove(photo.id)}
                            className="absolute -top-1 -right-1 w-5 h-5 bg-zinc-100 text-black rounded-full flex items-center justify-center shadow-lg border border-black"
                        >
                            <X size={12} strokeWidth={4} />
                        </button>
                    </div>
                ))}

                {photos.length < 9 && (
                    <button
                        onClick={() => fileRef.current?.click()}
                        className="aspect-square bg-zinc-800/50 border border-dashed border-zinc-700 rounded-xl flex flex-col items-center justify-center group hover:border-zinc-500 transition-all active:scale-95"
                    >
                        <Plus size={20} className="text-zinc-500 group-hover:text-white mb-1" />
                        <span className="text-[10px] text-zinc-600 font-bold uppercase">Add Photo</span>
                    </button>
                )}
            </div>

            <input
                type="file"
                ref={fileRef}
                onChange={handleFile}
                multiple
                accept="image/*"
                className="hidden"
            />

            <div className="flex items-center justify-between text-[10px] text-zinc-500 font-bold uppercase tracking-widest pl-1">
                <span>{photos.length} of 10 photos</span>
                {photos.length >= 3 && <span className="text-green-500">Min reached ✓</span>}
            </div>
        </div>
    );
};

export default PortfolioUploader;
