import React, { useState } from 'react';
import { Plus, Trash2, Edit3, DollarSign, Clock, X } from 'lucide-react';

const ServiceManager = ({ services = [], onAdd, onDelete, onUpdate }) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newService, setNewService] = useState({ name: '', price: '', duration: '' });

    const handleAdd = () => {
        if (!newService.name) return;
        onAdd({
            name: newService.name,
            price_min: parseFloat(newService.price) || 0,
            duration_minutes: parseInt(newService.duration) || 0
        });
        setNewService({ name: '', price: '', duration: '' });
        setIsAdding(false);
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Offered Services</h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="w-8 h-8 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center text-white"
                >
                    {isAdding ? <X size={16} /> : <Plus size={16} />}
                </button>
            </div>

            {isAdding && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-5 space-y-4 animate-in slide-in-from-top-2 duration-300">
                    <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                        <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Service Name</span>
                        <input
                            className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                            value={newService.name}
                            onChange={(e) => setNewService({ ...newService, name: e.target.value })}
                            placeholder="e.g. Highlight Treatment"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                            <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Price</span>
                            <div className="flex items-center">
                                <DollarSign size={14} className="text-zinc-500 mr-1" />
                                <input
                                    type="number"
                                    className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                                    value={newService.price}
                                    onChange={(e) => setNewService({ ...newService, price: e.target.value })}
                                    placeholder="0"
                                />
                            </div>
                        </div>
                        <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                            <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Min Duration</span>
                            <div className="flex items-center">
                                <Clock size={14} className="text-zinc-500 mr-1" />
                                <input
                                    type="number"
                                    className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                                    value={newService.duration}
                                    onChange={(e) => setNewService({ ...newService, duration: e.target.value })}
                                    placeholder="min"
                                />
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={handleAdd}
                        className="w-full h-12 bg-white text-black rounded-xl font-black text-sm"
                    >
                        Save Service
                    </button>
                </div>
            )}

            <div className="space-y-3">
                {services.map((service) => (
                    <div key={service.id} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 flex items-center justify-between group">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center">
                                <CheckCircle2 size={18} className="text-zinc-500" />
                            </div>
                            <div>
                                <h4 className="font-bold text-white text-sm">{service.name}</h4>
                                <div className="flex items-center gap-3 text-zinc-500 text-[10px] font-bold uppercase tracking-wider">
                                    <span className="flex items-center gap-1"><DollarSign size={10} /> {service.price_min || service.price}</span>
                                    <span className="flex items-center gap-1"><Clock size={10} /> {service.duration_minutes || service.duration}min</span>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => onDelete(service.id)}
                                className="w-9 h-9 bg-zinc-800/50 rounded-xl flex items-center justify-center text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-all"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Internal Import helper
import { CheckCircle2 } from 'lucide-react';

export default ServiceManager;
