import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import { getProviders } from '../api/client';
import { MessageCircle, Layout, ChevronDown } from 'lucide-react';

const HomePage = () => {
    const navigate = useNavigate();
    const [providers, setProviders] = useState([]);
    const [selectedProvider, setSelectedProvider] = useState("");

    useEffect(() => {
        getProviders().then(res => {
            setProviders(res.data);
            if (res.data.length > 0) setSelectedProvider(res.data[0].id);
        });
    }, []);

    return (
        <div className="flex-1 flex flex-col p-6 bg-white min-h-screen">
            <div className="mt-12 mb-16 text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg shadow-blue-200">
                    <span className="text-white text-3xl font-bold">P</span>
                </div>
                <h1 className="text-4xl font-black text-gray-900 tracking-tight">Proxie</h1>
                <p className="text-gray-500 font-medium">Your craft, represented</p>
            </div>

            <div className="space-y-10">
                {/* Consumer Section */}
                <section className="space-y-4">
                    <h2 className="text-xs font-black uppercase tracking-widest text-gray-400 ml-1">I need a service</h2>
                    <div className="space-y-3">
                        <button
                            onClick={() => navigate('/chat?role=consumer')}
                            className="w-full flex items-center justify-between p-5 bg-blue-600 text-white rounded-2xl shadow-lg shadow-blue-100 active:scale-[0.98] transition-all"
                        >
                            <div className="flex items-center space-x-4">
                                <div className="p-2 bg-white/20 rounded-lg">
                                    <MessageCircle size={24} />
                                </div>
                                <div className="text-left">
                                    <div className="font-bold text-lg">Chat with Agent</div>
                                    <div className="text-white/70 text-sm">Find and book instantly</div>
                                </div>
                            </div>
                        </button>
                        <button
                            onClick={() => navigate('/request/new')}
                            className="w-full flex items-center space-x-3 p-4 bg-gray-50 text-gray-600 rounded-2xl border border-gray-100 active:bg-gray-100 transition-colors"
                        >
                            <Layout size={18} />
                            <span className="font-bold">Use Forms</span>
                        </button>
                    </div>
                </section>

                {/* Provider Section */}
                <section className="space-y-4">
                    <div className="flex items-center justify-between ml-1">
                        <h2 className="text-xs font-black uppercase tracking-widest text-gray-400">I'm a provider</h2>
                        {providers.length > 0 && (
                            <div className="flex items-center text-[10px] font-bold text-gray-400 border border-gray-100 px-2 py-0.5 rounded-full">
                                TEST AS: {providers.find(p => p.id === selectedProvider)?.name.toUpperCase()}
                            </div>
                        )}
                    </div>

                    <div className="relative mb-3">
                        <select
                            className="w-full p-4 bg-gray-50 border border-gray-100 rounded-2xl font-bold text-gray-700 outline-none appearance-none"
                            value={selectedProvider}
                            onChange={(e) => setSelectedProvider(e.target.value)}
                        >
                            {providers.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={18} />
                    </div>

                    <div className="space-y-3">
                        <button
                            onClick={() => navigate(`/chat?role=provider&provider_id=${selectedProvider}`)}
                            className="w-full flex items-center justify-between p-5 bg-gray-900 text-white rounded-2xl shadow-lg shadow-gray-200 active:scale-[0.98] transition-all"
                        >
                            <div className="flex items-center space-x-4">
                                <div className="p-2 bg-white/10 rounded-lg">
                                    <MessageCircle size={24} />
                                </div>
                                <div className="text-left">
                                    <div className="font-bold text-lg">Chat with Agent</div>
                                    <div className="text-white/50 text-sm">Manage leads and offers</div>
                                </div>
                            </div>
                        </button>
                        <button
                            onClick={() => navigate('/provider')}
                            className="w-full flex items-center space-x-3 p-4 bg-gray-50 text-gray-600 rounded-2xl border border-gray-100 active:bg-gray-100 transition-colors"
                        >
                            <Layout size={18} />
                            <span className="font-bold">Use Dashboard</span>
                        </button>
                    </div>
                </section>
            </div>

            <footer className="mt-auto py-8 text-center text-gray-300 text-sm font-medium">
                PROXIE PLATFORM &copy; 2026
            </footer>
        </div>
    );
};

export default HomePage;
