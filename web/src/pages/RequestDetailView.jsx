import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, MapPin, Clock, DollarSign, Edit3, XCircle,
    MessageSquare, ArrowRight, Share2, Info, AlertTriangle, CheckCircle2
} from 'lucide-react';
import { getRequest, cancelRequest } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusTimeline from '../components/requests/StatusTimeline';
import MediaGallery from '../components/shared/MediaGallery';
import MediaViewer from '../components/MediaViewer';

const RequestDetailView = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [request, setRequest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isCancelling, setIsCancelling] = useState(false);
    const [showCancelConfirm, setShowCancelConfirm] = useState(false);
    const [viewerState, setViewerState] = useState({ isOpen: false, media: [], index: 0 });

    useEffect(() => {
        fetchRequest();
    }, [id]);

    const fetchRequest = async () => {
        try {
            setLoading(true);
            const res = await getRequest(id);
            setRequest(res.data);
        } catch (err) {
            console.error("Error fetching request:", err);
            setError("Could not load request details. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = async () => {
        try {
            setIsCancelling(true);
            await cancelRequest(id);
            fetchRequest(); // Refresh to show cancelled status
            setShowCancelConfirm(false);
        } catch (err) {
            console.error("Error cancelling request:", err);
            alert("Failed to cancel request. Please try again.");
        } finally {
            setIsCancelling(false);
        }
    };

    const canEdit = request?.status === 'matching' && (!request?.offer_count || request?.offer_count === 0);
    const canCancel = ['matching', 'pending'].includes(request?.status);

    if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;
    if (error) return (
        <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-8 text-center">
            <AlertTriangle size={48} className="text-red-500 mb-4" />
            <h2 className="text-xl font-black text-white mb-2">Error</h2>
            <p className="text-zinc-500 mb-6">{error}</p>
            <button onClick={() => navigate('/')} className="px-6 py-3 bg-zinc-900 rounded-2xl font-bold text-white">Back to Dashboard</button>
        </div>
    );

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white pb-32">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 px-4 py-6 bg-zinc-950/80 backdrop-blur-xl border-b border-white/5">
                <div className="max-w-[480px] mx-auto flex items-center justify-between">
                    <button onClick={() => navigate('/')} className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-white/5">
                        <ChevronLeft size={20} />
                    </button>
                    <h1 className="font-black tracking-tight text-lg">Request Details</h1>
                    <button className="w-10 h-10 bg-zinc-900 rounded-full flex items-center justify-center border border-white/5">
                        <Share2 size={18} />
                    </button>
                </div>
            </header>

            <main className="max-w-[480px] mx-auto w-full px-5 pt-28 space-y-8">
                {/* Status Hero */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${request.status === 'matching' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                                request.status === 'pending' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
                                    request.status === 'completed' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                                        'bg-zinc-800 text-zinc-400 border-white/5'
                            }`}>
                            {request.status}
                        </span>
                        <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
                            ID: {id.slice(0, 8)}
                        </span>
                    </div>
                    <h2 className="text-4xl font-black tracking-tight mb-2">{request.service_type}</h2>
                    <p className="text-zinc-400 font-medium italic text-lg leading-relaxed">
                        "{request.raw_input}"
                    </p>
                </section>

                {/* Gallery */}
                <MediaGallery
                    media={request.media}
                    onOpenViewer={(index) => setViewerState({ isOpen: true, media: request.media, index })}
                />

                {/* Details Grid */}
                <section className="grid grid-cols-2 gap-3">
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-5">
                        <MapPin size={18} className="text-blue-400 mb-3" />
                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Location</p>
                        <p className="font-bold text-white">{request.location?.city}</p>
                        {request.location?.neighborhood && <p className="text-xs text-zinc-500">{request.location?.neighborhood}</p>}
                    </div>
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-5">
                        <Clock size={18} className="text-purple-400 mb-3" />
                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Timing</p>
                        <p className="font-bold text-white capitalize">{request.timing?.urgency || 'Flexible'}</p>
                    </div>
                    <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-5 col-span-2 flex items-center justify-between">
                        <div>
                            <DollarSign size={18} className="text-green-400 mb-3" />
                            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Budget Range</p>
                            <p className="text-xl font-black text-white">${request.budget?.min} — ${request.budget?.max}</p>
                        </div>
                        <div className="text-right">
                            <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest block mb-1">Status</span>
                            {request.offer_count ? (
                                <span className="text-blue-400 font-black">{request.offer_count} OFFERS</span>
                            ) : (
                                <span className="text-amber-400 font-black">MATCHING</span>
                            )}
                        </div>
                    </div>
                </section>

                {/* Timeline */}
                <section className="bg-zinc-900/30 border border-white/5 rounded-3xl p-6">
                    <StatusTimeline history={request.status_history} />
                </section>

                {/* Actions Section */}
                {(canEdit || canCancel) && (
                    <section className="space-y-3">
                        {canEdit && (
                            <button
                                onClick={() => navigate('/chat', { state: { edit_request: request } })}
                                className="w-full h-14 bg-zinc-900 border border-white/10 rounded-2xl flex items-center justify-center gap-3 font-bold hover:bg-zinc-800 transition-all"
                            >
                                <Edit3 size={18} className="text-zinc-400" />
                                Edit Request Details
                            </button>
                        )}
                        {canCancel && (
                            <button
                                onClick={() => setShowCancelConfirm(true)}
                                className="w-full h-14 bg-red-500/5 border border-red-500/10 rounded-2xl flex items-center justify-center gap-3 font-bold text-red-500 hover:bg-red-500/10 transition-all"
                            >
                                <XCircle size={18} />
                                Cancel Request
                            </button>
                        )}
                    </section>
                )}
            </main>

            {/* Sticky Action Footer */}
            {request.status === 'pending' && (
                <div className="fixed bottom-0 left-0 right-0 p-5 bg-zinc-950/80 backdrop-blur-xl border-t border-white/5 z-40">
                    <div className="max-w-[480px] mx-auto">
                        <button
                            onClick={() => navigate(`/request/${id}/offers`)}
                            className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-white/10 active:scale-95 transition-all"
                        >
                            View All Offers <ArrowRight size={20} />
                        </button>
                    </div>
                </div>
            )}

            {/* Cancel Confirmation Modal */}
            {showCancelConfirm && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
                    <div className="bg-zinc-900 border border-zinc-800 rounded-[2.5rem] p-8 w-full max-w-sm shadow-2xl animate-in fade-in zoom-in duration-300">
                        <div className="w-16 h-16 bg-red-500/10 rounded-2xl flex items-center justify-center mb-6 border border-red-500/20">
                            <XCircle size={32} className="text-red-500" />
                        </div>
                        <h3 className="text-2xl font-black text-white mb-3 tracking-tight">Wait!</h3>
                        <p className="text-zinc-500 text-sm mb-8 leading-relaxed font-medium">
                            Are you sure you want to cancel this request? This action cannot be undone and providers will no longer be able to send offers.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowCancelConfirm(false)}
                                className="flex-1 h-14 bg-zinc-800 rounded-2xl font-bold text-white hover:bg-zinc-700 transition-all"
                            >
                                Nevermind
                            </button>
                            <button
                                onClick={handleCancel}
                                disabled={isCancelling}
                                className="flex-1 h-14 bg-red-500 text-white rounded-2xl font-black hover:bg-red-600 transition-all shadow-lg shadow-red-500/20 disabled:opacity-50"
                            >
                                {isCancelling ? '...' : 'Yes, Cancel'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

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

export default RequestDetailView;
