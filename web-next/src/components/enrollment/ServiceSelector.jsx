"use client";

import React, { useState } from 'react';
import {
    Scissors, Wind, Wrench, Zap, Camera,
    Check, ChevronRight, Briefcase
} from 'lucide-react';

const icons = {
    Scissors, Wind, Wrench, Zap, Camera, Briefcase
};

const ServiceSelector = ({ catalog, selectedServices = [], onSelect }) => {
    const [step, setStep] = useState('categories'); // 'categories' or 'services'
    const [selectedCategory, setSelectedCategory] = useState(null);

    const toggleService = (service) => {
        const isSelected = selectedServices.find(s => s.id === service.id);
        if (isSelected) {
            onSelect(selectedServices.filter(s => s.id !== service.id));
        } else {
            onSelect([...selectedServices, { ...service, categoryId: selectedCategory.id }]);
        }
    };

    if (step === 'categories' || !selectedCategory) {
        return (
            <div className="bg-zinc-900 border border-zinc-800 rounded-[2rem] p-6 w-full max-w-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
                <h3 className="text-white font-black text-lg mb-4 flex items-center">
                    <Briefcase className="mr-2 text-zinc-500" size={20} />
                    What do you offer?
                </h3>
                <div className="grid grid-cols-2 gap-3">
                    {catalog?.map((cat) => {
                        const Icon = icons[cat.icon] || Briefcase;
                        return (
                            <button
                                key={cat.id}
                                onClick={() => {
                                    setSelectedCategory(cat);
                                    setStep('services');
                                }}
                                className="flex flex-col items-center justify-center p-4 bg-zinc-800/50 border border-zinc-700/50 rounded-2xl hover:border-zinc-500 hover:bg-zinc-800 transition-all active:scale-95 group cursor-pointer"
                            >
                                <div className="w-10 h-10 rounded-xl bg-zinc-900 flex items-center justify-center mb-2 group-hover:bg-zinc-700 transition-colors">
                                    <Icon size={20} className="text-white" />
                                </div>
                                <span className="text-zinc-300 text-xs font-bold text-center">{cat.name}</span>
                            </button>
                        );
                    })}
                </div>
            </div>
        );
    }

    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-[2rem] p-6 w-full max-w-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-4">
                <button
                    onClick={() => setStep('categories')}
                    className="text-zinc-500 hover:text-white transition-colors cursor-pointer"
                >
                    <ChevronRight size={20} className="rotate-180" />
                </button>
                <h3 className="text-white font-black text-lg">{selectedCategory?.name}</h3>
                <div className="w-5" />
            </div>

            <div className="space-y-2 mb-6 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                {selectedCategory?.services?.map((svc) => {
                    const isSelected = selectedServices?.find(s => s.id === svc.id);
                    return (
                        <button
                            key={svc.id}
                            onClick={() => toggleService(svc)}
                            className={`w-full flex items-center justify-between p-4 rounded-2xl border transition-all cursor-pointer ${isSelected
                                ? 'bg-white border-white text-black'
                                : 'bg-zinc-800/30 border-zinc-700/50 text-zinc-400 hover:border-zinc-600'
                                }`}
                        >
                            <div className="text-left">
                                <span className="text-sm font-black block">{svc.name}</span>
                                <span className={`text-[10px] ${isSelected ? 'text-zinc-600' : 'text-zinc-500'}`}>
                                    {svc.typical_price_range ? `$${svc.typical_price_range.min}-${svc.typical_price_range.max}` : 'Custom pricing'}
                                </span>
                            </div>
                            {isSelected && <Check size={16} />}
                        </button>
                    );
                })}
            </div>

            <button
                onClick={() => setStep('categories')}
                className="w-full h-12 bg-white text-black rounded-full font-black text-sm active:scale-95 transition-all cursor-pointer"
            >
                Done with {selectedCategory?.name}
            </button>
        </div>
    );
};

export default ServiceSelector;
