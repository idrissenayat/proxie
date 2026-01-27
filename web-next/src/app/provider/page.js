"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
    Briefcase, MapPin, DollarSign, ChevronRight,
    Star, Clock, Filter, Search, User,
    MessageSquare, Bell, TrendingUp, CheckCircle2,
    ImageIcon, PlayCircle, Plus, Mic, AudioWaveform, X
} from 'lucide-react';
import { getProviders, getRequests } from '@/lib/api';
import LoadingSpinner from '@/components/LoadingSpinner';

const LeadCard = ({ lead, selectedProviderId, onClick }) => {
    const isNew = !lead.viewed_by_current_provider;

    return (
        <div
            onClick={onClick}
            className="group bg-zinc-900 border border-zinc-800 rounded-2xl p-4 hover:border-blue-500/50 transition-all cursor-pointer"
        >
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black uppercase tracking-wider rounded-lg border border-blue-500/20">
                        {lead.service_type}
                    </span>
                    {isNew && <span className="w-2 h-2 bg-blue-500 rounded-full"></span>}
                </div>
                <div className="text-green-400 text-sm font-black flex items-center">
                    <DollarSign size={14} /> {lead.budget?.min || 0}-{lead.budget?.max || 0}
                </div>
            </div>

            <h3 className="text-base font-bold text-white mb-2 leading-tight group-hover:text-blue-400 transition-colors">
                {lead.raw_input}
            </h3>

            <div className="flex items-center gap-4 text-xs text-zinc-500 mb-4">
                <div className="flex items-center"><MapPin size={14} className="mr-1" /> {lead.location?.city}</div>
                <div className="flex items-center"><Clock size={14} className="mr-1" /> {lead.timing?.preference || "Flexible"}</div>
            </div>

            {lead.media && lead.media.length > 0 && (
                <div className="flex gap-2 mb-4">
                    {lead.media.slice(0, 3).map((m, i) => (
                        <div key={i} className="w-12 h-12 rounded-lg bg-zinc-800 overflow-hidden border border-zinc-800">
                            <img src={m.preview || m.url} alt="Lead photo" className="w-full h-full object-cover" />
                        </div>
                    ))}
                    {lead.media.length > 3 && (
                        <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center text-[10px] font-black text-zinc-500">
                            +{lead.media.length - 3}
                        </div>
                    )}
                </div>
            )}

            <div className="flex items-center justify-between pt-2 border-t border-zinc-800/50">
                <span className="text-[10px] font-bold text-zinc-600 uppercase">Matched recently</span>
                <span className="text-xs font-black text-blue-400 flex items-center gap-1">
                    Details <ChevronRight size={14} />
                </span>
            </div>
        </div>
    );
};

export default function ProviderDashboard() {
    const router = useRouter();
    const [providers, setProviders] = useState([]);
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedProvider, setSelectedProvider] = useState(null);

    useEffect(() => {
        const fetchProviders = async () => {
            try {
                const provRes = await getProviders();
                setProviders(provRes.data);
                if (provRes.data.length > 0 && !selectedProvider) {
                    setSelectedProvider(provRes.data[0]);
                }
            } catch (error) {
                console.error("Error loading providers:", error);
            }
        };
        fetchProviders();
    }, []);

    useEffect(() => {
        const fetchLeads = async () => {
            if (!selectedProvider) return;
            try {
                const reqRes = await getRequests({
                    status: 'matching',
                    matching_provider_id: selectedProvider.id
                });
                setRequests(reqRes.data);
            } catch (error) {
                console.error("Error loading leads:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchLeads();
    }, [selectedProvider]);

    if (loading) return <div className="min-h-screen bg-black flex items-center justify-center"><LoadingSpinner /></div>;

    const stats = [
        { label: 'New Leads', value: requests.length, icon: Bell, color: 'text-blue-400', bg: 'bg-blue-400/10', path: '/provider' },
        { label: 'My Offers', value: '2', icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400/10', path: '/provider/offers' },
        { label: 'Upcoming', value: '5', icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-400/10', path: '/provider/offers' },
    ];

    return (
        <div className="flex flex-col min-h-screen bg-black text-white selection:bg-blue-500/30">
            {/* Header */}
            <header className="p-4 pt-6 bg-black/80 backdrop-blur-md sticky top-0 z-40 border-b border-zinc-900/50">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight">Provider Hub</h1>
                        <p className="text-zinc-500 text-xs font-medium">Representing your craft</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => router.push('/provider/profile')}
                            className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 cursor-pointer"
                        >
                            <User size={18} className="text-zinc-400" />
                        </button>
                        <button className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-800 relative cursor-pointer">
                            <Bell size={18} className="text-zinc-400" />
                            {requests.length > 0 && (
                                <span className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full border-2 border-black shadow-lg shadow-blue-500/20"></span>
                            )}
                        </button>
                    </div>
                </div>

                <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                    {providers.map(p => (
                        <button
                            key={p.id}
                            onClick={() => setSelectedProvider(p)}
                            className={`flex items-center gap-2 px-3 py-2 rounded-xl border transition-all whitespace-nowrap cursor-pointer ${selectedProvider?.id === p.id
                                ? 'bg-white text-black border-white'
                                : 'bg-zinc-900 text-zinc-400 border-zinc-800'
                                }`}
                        >
                            <span className="text-sm font-bold">{p.name}</span>
                        </button>
                    ))}
                </div>
            </header>

            <main className="flex-1 overflow-y-auto px-4 pb-32">
                {/* Stats Grid */}
                <section className="grid grid-cols-3 gap-3 my-6">
                    {stats.map((stat, i) => (
                        <div
                            key={i}
                            onClick={() => router.push(stat.path)}
                            className="bg-zinc-900/50 border border-zinc-900 rounded-2xl p-4 flex flex-col items-center text-center cursor-pointer hover:bg-zinc-900 transition-colors"
                        >
                            <div className={`w-10 h-10 ${stat.bg} ${stat.color} rounded-xl flex items-center justify-center mb-3`}>
                                <stat.icon size={20} />
                            </div>
                            <span className="text-2xl font-black text-white">{stat.value}</span>
                            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mt-1">{stat.label}</span>
                        </div>
                    ))}
                </section>

                <section className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-black text-white">Active Leads</h2>
                        <button className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs font-bold text-zinc-400 cursor-pointer">
                            <Filter size={14} /> Filter
                        </button>
                    </div>

                    <div className="space-y-4">
                        {requests.length === 0 ? (
                            <div className="py-20 text-center bg-zinc-900/30 rounded-3xl border border-dashed border-zinc-800">
                                <Search size={40} className="mx-auto text-zinc-800 mb-4" />
                                <p className="text-zinc-500 font-bold">No leads found</p>
                            </div>
                        ) : (
                            requests.map(req => (
                                <LeadCard
                                    key={req.id}
                                    lead={req}
                                    selectedProviderId={selectedProvider?.id}
                                    onClick={() => router.push(`/provider/request/${req.id}?provider_id=${selectedProvider?.id}`)}
                                />
                            ))
                        )}
                    </div>
                </section>
            </main>

            {/* Sticky Bottom Agent Bar */}
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black via-black to-transparent pt-8 z-40">
                <div className="max-w-[480px] mx-auto">
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={() => router.push('/chat?role=provider')}
                            className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center hover:bg-zinc-800 shrink-0 shadow-lg cursor-pointer"
                        >
                            <Plus size={20} className="text-zinc-400" />
                        </button>

                        <div
                            onClick={() => router.push('/chat?role=provider')}
                            className="flex-1 flex items-center bg-zinc-900/90 backdrop-blur-md rounded-full border border-zinc-800 pl-5 pr-2 py-2 cursor-pointer"
                        >
                            <span className="flex-1 text-zinc-500 font-medium text-sm">Ask your agent anything...</span>
                            <div className="flex items-center space-x-1 ml-2">
                                <div className="w-9 h-9 bg-white rounded-full flex items-center justify-center">
                                    <AudioWaveform size={18} className="text-black" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
