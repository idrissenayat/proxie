import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, MapPin, Star, Clock, Briefcase, Share2,
    CheckCircle2, ArrowRight, MessageSquare, Award
} from 'lucide-react';
import { getProviderProfile, getProviderPortfolio } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import MediaGallery from '../components/shared/MediaGallery';
import MediaViewer from '../components/MediaViewer';
import ReviewsList from '../components/profile/ReviewsList';

const PublicProviderProfile = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [provider, setProvider] = useState(null);
    const [portfolio, setPortfolio] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewerState, setViewerState] = useState({ isOpen: false, media: [], index: 0 });

    useEffect(() => {
        const fetch = async () => {
            try {
                const [profRes, portRes] = await Promise.all([
                    getProviderProfile(id),
                    getProviderPortfolio(id)
                ]);
                setProvider(profRes.data);
                setPortfolio(portRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [id]);

    if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;
    if (!provider) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-red-500 font-bold">Provider not found</div>;

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white pb-32">
            {/* Immersive Header */}
            <div className="relative h-64 md:h-80 bg-zinc-900 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 to-transparent z-10" />
                {provider.profile_photo_url ? (
                    <img
                        src={provider.profile_photo_url}
                        alt={provider.name}
                        className="w-full h-full object-cover opacity-50"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center bg-zinc-800">
                        <Award size={80} className="text-zinc-700 opacity-20" />
                    </div>
                )}

                <button
                    onClick={() => navigate(-1)}
                    className="absolute top-6 left-4 w-10 h-10 bg-zinc-950/50 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center text-white z-20"
                >
                    <ChevronLeft size={20} />
                </button>
                <button
                    className="absolute top-6 right-4 w-10 h-10 bg-zinc-950/50 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center text-white z-20"
                >
                    <Share2 size={18} />
                </button>

                <div className="absolute inset-x-0 bottom-0 p-6 z-20 flex flex-col items-center">
                    <div className="w-24 h-24 bg-zinc-800 rounded-3xl border-4 border-zinc-950 overflow-hidden shadow-2xl mb-4">
                        {provider.profile_photo_url ? (
                            <img src={provider.profile_photo_url} alt={provider.name} className="w-full h-full object-cover" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-3xl font-black">{provider.name.charAt(0)}</div>
                        )}
                    </div>
                    <div className="text-center">
                        <h1 className="text-3xl font-black tracking-tight flex items-center justify-center gap-2">
                            {provider.business_name || provider.name}
                            {provider.verified && <CheckCircle2 size={24} className="text-blue-500 fill-blue-500/10" />}
                        </h1>
                        <p className="text-zinc-400 font-bold uppercase tracking-widest text-xs mt-1">
                            {provider.specializations?.join(' • ') || 'Service Professional'}
                        </p>
                    </div>
                </div>
            </div>

            <main className="max-w-[480px] mx-auto w-full px-5 pt-8 space-y-10">
                {/* Stats Grid */}
                <section className="grid grid-cols-3 gap-3">
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-4 text-center">
                        <div className="flex items-center justify-center gap-1 text-yellow-500 mb-1">
                            <Star size={14} className="fill-yellow-500" />
                            <span className="text-lg font-black text-white">{provider.rating || 0}</span>
                        </div>
                        <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">{provider.review_count || 0} Reviews</p>
                    </div>
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-4 text-center">
                        <div className="text-lg font-black text-white mb-1">{provider.jobs_completed || 0}</div>
                        <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">Jobs Done</p>
                    </div>
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-4 text-center">
                        <div className="text-lg font-black text-white mb-1">{provider.years_experience || 0}y</div>
                        <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">Experience</p>
                    </div>
                </section>

                {/* Bio */}
                <section>
                    <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-3">About</h3>
                    <p className="text-zinc-300 leading-relaxed font-medium">
                        {provider.bio || `Skilled professional providing ${provider.specializations?.join(', ') || 'expert'} services in ${provider.location?.city}.`}
                    </p>
                </section>

                {/* Portfolio */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Portfolio</h3>
                        <span className="text-[10px] font-bold text-zinc-600 uppercase tabular-nums">{portfolio.length} Items</span>
                    </div>
                    <MediaGallery
                        media={portfolio.map(p => ({ url: p.photo_url, caption: p.caption }))}
                        onOpenViewer={(index) => setViewerState({
                            isOpen: true,
                            media: portfolio.map(p => ({ url: p.photo_url, caption: p.caption })),
                            index
                        })}
                    />
                </section>

                {/* Reviews */}
                <section>
                    <ReviewsList reviews={[]} /> {/* Connect to real reviews API when available */}
                </section>
            </main>

            {/* CTA Footer */}
            <div className="fixed bottom-0 left-0 right-0 p-5 bg-zinc-950/80 backdrop-blur-xl border-t border-white/5 z-40">
                <div className="max-w-[480px] mx-auto">
                    <button
                        onClick={() => navigate('/chat', { state: { book_provider: provider } })}
                        className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-white/10 active:scale-95 transition-all"
                    >
                        Book Now <ArrowRight size={20} />
                    </button>
                </div>
            </div>

            {/* Media Viewer */}
            <MediaViewer
                isOpen={viewerState.isOpen}
                media={viewerState.media}
                index={viewerState.index}
                onClose={() => setViewerState({ ...viewerState, isOpen: false })}
            />
        </div>
    );
};

export default PublicProviderProfile;
