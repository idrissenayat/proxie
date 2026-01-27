import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
    MapPin, Clock, DollarSign, User, FileText,
    ChevronLeft, Info, HelpCircle, Sparkles,
    ArrowRight, MessageSquare, Camera
} from 'lucide-react';
import { getRequest, markLeadViewed } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import MediaViewer from '../components/MediaViewer';

const RequestDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [request, setRequest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [viewerState, setViewerState] = useState({ isOpen: false, media: [], index: 0 });
    const providerId = location.state?.providerId;

    useEffect(() => {
        const fetch = async () => {
            try {
                const res = await getRequest(id);
                setRequest(res.data);

                // Mark as viewed
                if (providerId) {
                    markLeadViewed(id, providerId).catch(console.error);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, [id, providerId]);

    if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;
    if (!request) return <div className="min-h-screen bg-zinc-950 p-8 text-center text-red-500 font-bold">Request not found</div>;

    // Specialist Analysis (if extended in Sprint 9)
    const specialist = request.specialist_analysis || request.requirements?.specialist_analysis;

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white pb-32">
            {/* Immersive Header / Gallery */}
            <div className="relative h-72 md:h-96 bg-zinc-900 border-b border-zinc-800">
                {request.media && request.media.length > 0 ? (
                    <div
                        className="w-full h-full cursor-zoom-in"
                        onClick={() => setViewerState({ isOpen: true, media: request.media, index: 0 })}
                    >
                        <img
                            src={request.media[0].url}
                            alt="Lead Preview"
                            className="w-full h-full object-cover opacity-60 hover:opacity-100 transition-opacity"
                        />
                        <div className="absolute inset-x-0 bottom-0 p-6 bg-gradient-to-t from-zinc-950 to-transparent">
                            <span className="bg-zinc-900/80 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-black uppercase tracking-widest border border-zinc-800">
                                {request.media.length} Photos Attached
                            </span>
                        </div>
                    </div>
                ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-900 text-zinc-700">
                        <Camera size={48} className="mb-3 opacity-20" />
                        <span className="text-xs font-bold uppercase tracking-widest opacity-30">No Media Provided</span>
                    </div>
                )}

                <button
                    onClick={() => navigate(-1)}
                    className="absolute top-6 left-4 w-10 h-10 bg-zinc-950/50 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center text-white"
                >
                    <ChevronLeft size={20} />
                </button>
            </div>

            <main className="px-5 pt-8 space-y-8 max-w-2xl mx-auto w-full">
                {/* Core Details */}
                <section>
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h1 className="text-3xl font-black tracking-tight mb-2">{request.service_type}</h1>
                            <div className="flex items-center gap-4 text-sm text-zinc-400 font-medium">
                                <span className="flex items-center"><MapPin size={16} className="mr-1.5 text-blue-500" /> {request.location?.city}</span>
                                <span className="flex items-center"><Clock size={16} className="mr-1.5 text-purple-500" /> {request.timing?.preference || "Flexible"}</span>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest block mb-1">Consumer Budget</span>
                            <span className="text-2xl font-black text-green-400 leading-none">${request.budget?.min} - ${request.budget?.max}</span>
                        </div>
                    </div>

                    <div className="bg-zinc-900/40 border border-zinc-900 rounded-2xl p-4 italic text-zinc-300 leading-relaxed text-sm">
                        "{request.raw_input}"
                    </div>
                </section>

                {/* Specialist Analysis Section */}
                {specialist && (
                    <section className="bg-blue-500/5 border border-blue-500/10 rounded-3xl p-6 relative overflow-hidden group">
                        <div className="absolute -right-8 -top-8 w-32 h-32 bg-blue-500/10 blur-3xl group-hover:bg-blue-500/20 transition-all rounded-full" />

                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                <Sparkles size={16} className="text-blue-400" />
                            </div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-blue-400">Proxie Specialist Analysis</h3>
                        </div>

                        <div className="grid grid-cols-2 gap-y-4 gap-x-6">
                            {Object.entries(specialist).map(([key, value]) => {
                                if (typeof value === 'object' || key === 'notes') return null;
                                return (
                                    <div key={key}>
                                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">{key.replace('_', ' ')}</p>
                                        <p className="text-sm font-bold text-zinc-200">{String(value)}</p>
                                    </div>
                                );
                            })}
                        </div>

                        {specialist.notes && (
                            <div className="mt-4 pt-4 border-t border-blue-500/10 text-xs text-zinc-400 italic">
                                "{specialist.notes}"
                            </div>
                        )}
                    </section>
                )}

                {/* Consumer Profile Summary */}
                <section className="flex items-center gap-4 bg-zinc-900/50 rounded-2xl p-4 border border-zinc-900">
                    <div className="w-12 h-12 bg-zinc-800 rounded-xl flex items-center justify-center">
                        <User size={24} className="text-zinc-600" />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Client</p>
                        <p className="text-sm font-bold text-white leading-none mt-1">Anonymous Consumer</p>
                    </div>
                </section>
            </main>

            {/* Bottom Actions */}
            <div className="fixed bottom-0 left-0 right-0 p-5 bg-zinc-950/80 backdrop-blur-xl border-t border-zinc-900 z-40">
                <div className="max-w-2xl mx-auto flex gap-3">
                    <button
                        onClick={() => navigate('/chat?role=provider', { state: { targetLead: id, providerId } })}
                        className="flex-1 bg-zinc-900 border border-zinc-800 text-zinc-300 h-14 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-zinc-800 transition-all"
                    >
                        <MessageSquare size={18} /> Ask Agent
                    </button>
                    <button
                        onClick={() => navigate('/provider/offer/new', { state: { requestId: id, providerId } })}
                        className="flex-[2] bg-white text-black h-14 rounded-2xl font-black flex items-center justify-center gap-2 hover:bg-zinc-200 transition-all shadow-lg shadow-white/5 active:scale-95"
                    >
                        Make an Offer <ArrowRight size={18} />
                    </button>
                </div>
            </div>

            {/* Media Viewer */}
            {viewerState.isOpen && (
                <MediaViewer
                    isOpen={viewerState.isOpen}
                    media={viewerState.media}
                    index={viewerState.index}
                    onClose={() => setViewerState({ ...viewerState, isOpen: false })}
                />
            )}
        </div>
    );
};

export default RequestDetailPage;
