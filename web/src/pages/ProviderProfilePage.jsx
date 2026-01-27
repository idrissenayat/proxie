import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ChevronLeft, Settings, Award, Users, Briefcase,
    Star, MessageSquare, Plus, Edit3, CheckCircle2
} from 'lucide-react';
import {
    getProviderProfile, getProviderPortfolio, updateProviderProfile,
    addPortfolioPhoto, deletePortfolioPhoto
} from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import PortfolioManager from '../components/profile/PortfolioManager';
import ServiceManager from '../components/profile/ServiceManager';
import EditProfileModal from '../components/profile/EditProfileModal';
import ReviewsList from '../components/profile/ReviewsList';

const ProviderProfilePage = () => {
    const navigate = useNavigate();
    const providerId = localStorage.getItem('proxie_provider_id');
    const [provider, setProvider] = useState(null);
    const [portfolio, setPortfolio] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showEditModal, setShowEditModal] = useState(false);
    const [activeSection, setActiveSection] = useState('profile'); // 'profile', 'services', 'portfolio', 'reviews'

    useEffect(() => {
        if (!providerId) {
            navigate('/');
            return;
        }
        fetchData();
    }, [providerId]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [profRes, portRes] = await Promise.all([
                getProviderProfile(providerId),
                getProviderPortfolio(providerId)
            ]);
            setProvider(profRes.data);
            setPortfolio(portRes.data);
        } catch (err) {
            console.error("Error fetching provider data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateProfile = async (data) => {
        try {
            await updateProviderProfile(providerId, data);
            fetchData();
            setShowEditModal(false);
        } catch (err) {
            console.error("Error updating profile:", err);
            alert("Failed to update profile.");
        }
    };

    const handleAddPortfolio = async (photoData) => {
        try {
            await addPortfolioPhoto(providerId, photoData);
            fetchData();
        } catch (err) {
            console.error("Error adding portfolio photo:", err);
        }
    };

    const handleDeletePortfolio = async (photoId) => {
        try {
            await deletePortfolioPhoto(providerId, photoId);
            fetchData();
        } catch (err) {
            console.error("Error deleting portfolio photo:", err);
        }
    };

    if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;
    if (!provider) return null;

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white pb-10">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 px-4 py-6 bg-zinc-950/80 backdrop-blur-xl border-b border-white/5">
                <div className="max-w-[480px] mx-auto flex items-center justify-between">
                    <button onClick={() => navigate('/provider')} className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-white/5">
                        <ChevronLeft size={20} />
                    </button>
                    <h1 className="font-black tracking-tight text-lg">My Professional Profile</h1>
                    <button className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-white/5">
                        <Settings size={18} />
                    </button>
                </div>
            </header>

            <main className="max-w-[480px] mx-auto w-full px-5 pt-28 space-y-8">
                {/* Hero Profile */}
                <section className="relative group">
                    <div className="flex items-center gap-5">
                        <div className="relative">
                            <div className="w-24 h-24 bg-zinc-900 rounded-[2.5rem] border-2 border-white/5 overflow-hidden shadow-2xl">
                                {provider.profile_photo_url ? (
                                    <img src={provider.profile_photo_url} alt={provider.name} className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-3xl font-black">{provider.name.charAt(0)}</div>
                                )}
                            </div>
                            <button
                                onClick={() => setShowEditModal(true)}
                                className="absolute -bottom-1 -right-1 w-8 h-8 bg-white text-black rounded-xl flex items-center justify-center shadow-lg active:scale-95 transition-all"
                            >
                                <Edit3 size={14} />
                            </button>
                        </div>
                        <div className="flex-1">
                            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
                                {provider.name}
                                {provider.verified && <CheckCircle2 size={20} className="text-blue-500" />}
                            </h2>
                            <p className="text-zinc-500 font-bold uppercase tracking-widest text-[10px] mb-2">
                                {provider.business_name || 'Individual Professional'}
                            </p>
                            <div className="flex items-center gap-4">
                                <span className="flex items-center gap-1.5 text-xs font-bold text-zinc-400">
                                    <Star size={14} className="text-yellow-500 fill-yellow-500/10" /> {provider.rating}
                                </span>
                                <span className="flex items-center gap-1.5 text-xs font-bold text-zinc-400">
                                    <Users size={14} className="text-blue-500" /> {provider.review_count} Reviews
                                </span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Performance Stats Cards */}
                <section className="grid grid-cols-2 gap-3">
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-5 flex flex-col items-center text-center">
                        <span className="text-[28px] font-black text-white leading-none mb-2">{provider.jobs_completed || 0}</span>
                        <span className="text-[10px] font-black text-zinc-600 uppercase tracking-widest">Jobs Completed</span>
                    </div>
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-5 flex flex-col items-center text-center">
                        <span className="text-[28px] font-black text-white leading-none mb-2">{provider.response_rate || 100}%</span>
                        <span className="text-[10px] font-black text-zinc-600 uppercase tracking-widest">Response Rate</span>
                    </div>
                </section>

                {/* Navigation Tabs */}
                <section className="flex bg-zinc-900 rounded-2xl p-1.5 border border-white/5">
                    {[
                        { id: 'profile', icon: Award, label: 'Info' },
                        { id: 'services', icon: Briefcase, label: 'Services' },
                        { id: 'portfolio', icon: Plus, label: 'Portfolio' },
                        { id: 'reviews', icon: MessageSquare, label: 'Reviews' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveSection(tab.id)}
                            className={`flex-1 py-3 px-2 rounded-xl flex flex-col items-center gap-1 transition-all ${activeSection === tab.id ? 'bg-zinc-800 text-white shadow-xl' : 'text-zinc-600 hover:text-zinc-400'
                                }`}
                        >
                            <tab.icon size={18} />
                            <span className="text-[10px] font-bold uppercase tracking-wider">{tab.label}</span>
                        </button>
                    ))}
                </section>

                {/* Tab Content */}
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {activeSection === 'profile' && (
                        <div className="space-y-6">
                            <div className="bg-zinc-900/30 border border-white/5 rounded-3xl p-6">
                                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-3">Bio</h3>
                                <p className="text-sm font-medium text-zinc-300 leading-relaxed italic">
                                    "{provider.bio || 'No bio added yet. Tell your clients about your expertise!'}"
                                </p>
                            </div>
                            <div className="bg-zinc-900/30 border border-white/5 rounded-3xl p-6">
                                <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-3">Professional Info</h3>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs font-bold text-zinc-600 uppercase tracking-widest">Experience</span>
                                        <span className="text-sm font-black text-white">{provider.years_experience || 0} Years</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs font-bold text-zinc-600 uppercase tracking-widest">Service Area</span>
                                        <span className="text-sm font-black text-white">{provider.location?.city || 'Not set'}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs font-bold text-zinc-600 uppercase tracking-widest">Specializations</span>
                                        <div className="flex gap-2 flex-wrap justify-end max-w-[200px]">
                                            {provider.specializations?.map((s, i) => (
                                                <span key={i} className="px-2 py-0.5 bg-zinc-800 rounded-md text-[10px] font-black text-zinc-400 capitalize">{s}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeSection === 'services' && (
                        <ServiceManager
                            services={provider.services || []}
                            onAdd={(newS) => console.log('Add service', newS)} // Connect to API
                            onDelete={(id) => console.log('Delete service', id)} // Connect to API
                        />
                    )}

                    {activeSection === 'portfolio' && (
                        <PortfolioManager
                            photos={portfolio}
                            onAdd={handleAddPortfolio}
                            onDelete={handleDeletePortfolio}
                        />
                    )}

                    {activeSection === 'reviews' && (
                        <ReviewsList reviews={[]} />
                    )}
                </div>

                {/* Public View Toggle */}
                <section>
                    <button
                        onClick={() => navigate(`/providers/${providerId}`)}
                        className="w-full h-14 bg-zinc-900 border border-blue-500/20 text-blue-400 rounded-2xl flex items-center justify-center gap-3 font-bold hover:bg-zinc-800 transition-all"
                    >
                        View Public Profile
                    </button>
                </section>
            </main>

            {/* Edit Modal */}
            {showEditModal && (
                <EditProfileModal
                    provider={provider}
                    onClose={() => setShowEditModal(false)}
                    onSave={handleUpdateProfile}
                />
            )}
        </div>
    );
};

export default ProviderProfilePage;
