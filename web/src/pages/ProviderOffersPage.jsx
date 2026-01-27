import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    ChevronLeft, Search, Filter, Clock,
    CheckCircle2, XCircle, AlertCircle,
    ChevronRight, MapPin, DollarSign
} from 'lucide-react';
import { getProviderOffers } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const ProviderOffersPage = () => {
    const navigate = useNavigate();
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeFilter, setActiveFilter] = useState('all');

    useEffect(() => {
        const fetch = async () => {
            try {
                // In a real app we'd fetch for a specific provider
                // For MVP, we fetch all and show the status
                // const res = await getProviderOffers('provider-uuid');
                // Mocking API for now
                const mockOffers = [
                    {
                        id: '1',
                        status: 'pending',
                        price: 75,
                        created_at: '2026-01-25T10:00:00Z',
                        request: { service_type: 'Curly Bob Haircut', city: 'Brooklyn' }
                    },
                    {
                        id: '2',
                        status: 'accepted',
                        price: 150,
                        created_at: '2026-01-24T15:00:00Z',
                        request: { service_type: 'Balayage', city: 'Park Slope' }
                    }
                ];
                setOffers(mockOffers);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, []);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'accepted': return <CheckCircle2 size={16} className="text-green-400" />;
            case 'pending': return <Clock size={16} className="text-amber-400" />;
            case 'declined': return <XCircle size={16} className="text-red-400" />;
            default: return <AlertCircle size={16} className="text-zinc-500" />;
        }
    };

    const filteredOffers = offers.filter(o => activeFilter === 'all' || o.status === activeFilter);

    if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white font-sans">
            <header className="p-4 pt-6 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-40 border-b border-zinc-900/50">
                <div className="flex items-center gap-4 mb-4">
                    <button onClick={() => navigate(-1)} className="text-zinc-500 hover:text-white transition-colors">
                        <ChevronLeft />
                    </button>
                    <h1 className="text-xl font-black">My Submitted Offers</h1>
                </div>

                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                    {['all', 'pending', 'accepted', 'declined'].map(f => (
                        <button
                            key={f}
                            onClick={() => setActiveFilter(f)}
                            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider border transition-all ${activeFilter === f ? 'bg-white text-zinc-950 border-white' : 'bg-zinc-900 text-zinc-500 border-zinc-800'
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </header>

            <main className="p-4 space-y-4">
                {filteredOffers.length === 0 ? (
                    <div className="py-20 text-center">
                        <AlertCircle size={48} className="mx-auto text-zinc-800 mb-4" />
                        <p className="text-zinc-500 font-bold">No offers found</p>
                    </div>
                ) : (
                    filteredOffers.map(offer => (
                        <div
                            key={offer.id}
                            className="bg-zinc-900 border border-zinc-900 rounded-3xl p-5 hover:border-zinc-700 transition-colors cursor-pointer group"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center">
                                        <Briefcase size={20} className="text-zinc-500" />
                                    </div>
                                    <div>
                                        <h3 className="font-black text-white group-hover:text-blue-400 transition-colors uppercase text-sm tracking-tight leading-tight">
                                            {offer.request.service_type}
                                        </h3>
                                        <div className="flex items-center text-[10px] text-zinc-500 font-bold uppercase tracking-widest mt-1">
                                            <MapPin size={10} className="mr-1" /> {offer.request.city}
                                        </div>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800/50 rounded-full text-[10px] font-black uppercase tracking-widest border border-zinc-800`}>
                                    {getStatusIcon(offer.status)}
                                    <span className={
                                        offer.status === 'accepted' ? 'text-green-400' :
                                            offer.status === 'pending' ? 'text-amber-400' : 'text-zinc-400'
                                    }>{offer.status}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between pt-4 border-t border-zinc-800/50">
                                <div className="flex items-center gap-4 text-xs font-black">
                                    <div className="flex items-center text-green-400">
                                        <DollarSign size={14} /> {offer.price}
                                    </div>
                                    <div className="text-zinc-600">
                                        {new Date(offer.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                                <button className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-500 group-hover:bg-white group-hover:text-black transition-all">
                                    <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </main>
        </div>
    );
};

export default ProviderOffersPage;
