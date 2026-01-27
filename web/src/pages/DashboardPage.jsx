import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Plus, Mic, AudioWaveform, Search, ArrowRight,
    MapPin, Star, Clock, DollarSign, ChevronRight,
    User, Briefcase, Sparkles, Camera, Image, Video, X,
    MessageSquare, Calendar, CheckCircle2
} from 'lucide-react';
import { getProviders, getRequests, sendChatMessage, getConsumerRequests, getEnrollment, startEnrollment } from '../api/client';
import CameraCapture from '../components/CameraCapture';
import RequestSection from '../components/dashboard/RequestSection';

const getOrCreateConsumerId = () => {
    let id = localStorage.getItem('proxie_consumer_id');
    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('proxie_consumer_id', id);
    }
    return id;
};

const DashboardPage = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('demand'); // 'demand' or 'supply'
    const [input, setInput] = useState('');
    const [isVoiceMode, setIsVoiceMode] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [providers, setProviders] = useState([]);
    const [requests, setRequests] = useState([]);
    const [consumerRequests, setConsumerRequests] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isProviderEnrolled, setIsProviderEnrolled] = useState(false);
    const [enrollmentStatus, setEnrollmentStatus] = useState(null);
    const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
    const [selectedMedia, setSelectedMedia] = useState([]);
    const [showCamera, setShowCamera] = useState(false);
    const fileInputRef = useRef(null);
    const videoInputRef = useRef(null);
    const recognitionRef = useRef(null);

    useEffect(() => {
        const consumerId = getOrCreateConsumerId();

        // Load data
        const fetchData = async () => {
            try {
                // Check provider status
                const providerId = localStorage.getItem('proxie_provider_id');
                const existingEnrollmentId = localStorage.getItem('proxie_enrollment_id');

                if (providerId) {
                    setIsProviderEnrolled(true);
                } else if (existingEnrollmentId) {
                    try {
                        const enRes = await getEnrollment(existingEnrollmentId);
                        setEnrollmentStatus(enRes.data.status);
                        if (enRes.data.status === 'verified') {
                            setIsProviderEnrolled(true);
                            if (enRes.data.provider_id) {
                                localStorage.setItem('proxie_provider_id', enRes.data.provider_id);
                            }
                        }
                    } catch (e) {
                        console.error("Error fetching enrollment:", e);
                    }
                }

                const provRes = await getProviders();
                setProviders(provRes.data.slice(0, 5));

                const reqRes = await getRequests({ status: 'matching' });
                setRequests(reqRes.data.slice(0, 5));

                const conRes = await getConsumerRequests(consumerId);
                setConsumerRequests(conRes.data);
            } catch (err) {
                console.error("Error fetching dashboard data:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();

        // Setup speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                handleSubmit(transcript);
                setIsListening(false);
            };
            recognition.onerror = () => setIsListening(false);
            recognition.onend = () => setIsListening(false);
            recognitionRef.current = recognition;
        }
    }, []);

    const handleSubmit = async (text) => {
        const query = text || input;
        if (!query.trim() && selectedMedia.length === 0) return;

        // Navigate to chat with pre-filled message and media
        let role = activeTab === 'demand' ? 'consumer' : 'provider';

        // If provider tab is active but not enrolled, change role to enrollment
        if (role === 'provider' && !isProviderEnrolled) {
            role = 'enrollment';
        }

        if (selectedMedia.length > 0) {
            sessionStorage.setItem('proxie_initial_media', JSON.stringify(selectedMedia));
        }

        navigate(`/chat?role=${role}&initial=${encodeURIComponent(query)}`);
    };

    const handleFileSelect = (e, type) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (readerEvent) => {
                setSelectedMedia(prev => [...prev, {
                    id: Date.now() + Math.random(),
                    type: type,
                    data: readerEvent.target.result.split(',')[1],
                    mime_type: file.type,
                    preview: readerEvent.target.result
                }]);
            };
            reader.readAsDataURL(file);
        });
        setShowAttachmentMenu(false);
    };

    const handleCameraCapture = (dataUrl) => {
        setSelectedMedia(prev => [...prev, {
            id: Date.now(),
            type: 'image',
            data: dataUrl.split(',')[1],
            mime_type: 'image/jpeg',
            preview: dataUrl
        }]);
    };

    const removeMedia = (id) => {
        setSelectedMedia(prev => prev.filter(m => m.id !== id));
    };

    const toggleVoiceMode = () => {
        if (isVoiceMode) {
            setIsVoiceMode(false);
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            setIsVoiceMode(true);
            setIsListening(true);
            recognitionRef.current?.start();
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white">
            {/* Header */}
            <header className="p-4 pt-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight">Proxie</h1>
                        <p className="text-zinc-500 text-xs font-medium">Your craft, represented</p>
                    </div>
                    <button className="w-10 h-10 bg-zinc-800 rounded-full flex items-center justify-center border border-zinc-700">
                        <User size={18} className="text-zinc-400" />
                    </button>
                </div>

                {/* Segmented Control */}
                <div className="flex bg-zinc-900 rounded-xl p-1 border border-zinc-800">
                    <button
                        onClick={() => setActiveTab('demand')}
                        className={`flex-1 py-3 px-4 rounded-lg font-bold text-sm transition-all flex items-center justify-center space-x-2 ${activeTab === 'demand'
                            ? 'bg-white text-black shadow-lg'
                            : 'text-zinc-400 hover:text-white'
                            }`}
                    >
                        <Search size={16} />
                        <span>Find Services</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('supply')}
                        className={`flex-1 py-3 px-4 rounded-lg font-bold text-sm transition-all flex items-center justify-center space-x-2 ${activeTab === 'supply'
                            ? 'bg-white text-black shadow-lg'
                            : 'text-zinc-400 hover:text-white'
                            }`}
                    >
                        <Briefcase size={16} />
                        <span>Get Leads</span>
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto px-4 pb-32">
                {activeTab === 'demand' ? (
                    <>
                        {/* Quick Actions */}
                        <section className="mb-6">
                            <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-3">Popular Services</h2>
                            <div className="flex space-x-2 overflow-x-auto scrollbar-hide pb-2">
                                {['Haircut', 'Cleaning', 'Plumbing', 'Photography', 'Tutoring'].map((service) => (
                                    <button
                                        key={service}
                                        onClick={() => setInput(`I need a ${service.toLowerCase()}`)}
                                        className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-full text-sm font-medium text-zinc-300 hover:bg-zinc-800 hover:border-zinc-700 transition-colors whitespace-nowrap"
                                    >
                                        {service}
                                    </button>
                                ))}
                            </div>
                        </section>

                        <section className="mt-8 space-y-8">
                            <div className="border-b border-zinc-900 pb-2">
                                <h2 className="text-xl font-black text-white">My Requests</h2>
                            </div>

                            <RequestSection
                                title="Open"
                                icon={Clock}
                                type="open"
                                requests={consumerRequests?.requests?.open}
                            />

                            <RequestSection
                                title="Pending"
                                icon={MessageSquare}
                                type="pending"
                                requests={consumerRequests?.requests?.pending}
                                onViewAll={() => navigate('/requests?status=pending')}
                            />

                            <RequestSection
                                title="Upcoming"
                                icon={Calendar}
                                type="upcoming"
                                requests={consumerRequests?.requests?.upcoming}
                            />

                            <RequestSection
                                title="Recently Completed"
                                icon={CheckCircle2}
                                type="completed"
                                requests={consumerRequests?.requests?.completed}
                                onViewAll={() => navigate('/bookings?status=completed')}
                            />

                            {consumerRequests &&
                                consumerRequests.counts?.open === 0 &&
                                consumerRequests.counts?.pending === 0 &&
                                consumerRequests.counts?.upcoming === 0 &&
                                consumerRequests.counts?.completed === 0 && (
                                    <div className="text-center py-16 px-6 bg-zinc-900/20 border border-dashed border-zinc-800 rounded-[2rem]">
                                        <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-zinc-800">
                                            <Briefcase size={24} className="text-zinc-600" />
                                        </div>
                                        <h3 className="text-lg font-bold text-white mb-2">No requests yet</h3>
                                        <p className="text-zinc-500 text-sm mb-6 max-w-[200px] mx-auto leading-relaxed">
                                            Tap a service above or ask your agent to find what you need.
                                        </p>
                                        <button
                                            onClick={() => document.querySelector('input').focus()}
                                            className="bg-white text-black h-11 px-8 rounded-full font-black text-sm active:scale-95 transition-all"
                                        >
                                            Start a Request
                                        </button>
                                    </div>
                                )}
                        </section>
                    </>
                ) : (
                    <>
                        {/* Provider View */}
                        {!isProviderEnrolled ? (
                            <section className="animate-in fade-in slide-in-from-bottom-8 duration-1000">
                                <div className="bg-zinc-900 border-2 border-zinc-800 rounded-[3rem] p-10 shadow-2xl relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 blur-[100px] rounded-full -mr-32 -mt-32" />
                                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 blur-[100px] rounded-full -ml-32 -mb-32" />

                                    <div className="relative z-10 text-center">
                                        <div className="w-24 h-24 bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-[2.5rem] flex items-center justify-center mx-auto mb-8 border border-zinc-700 shadow-xl group-hover:scale-110 transition-transform duration-500">
                                            <Briefcase size={40} className="text-white" />
                                        </div>

                                        <h2 className="text-4xl font-black text-white mb-4 tracking-tight leading-tight text-center">
                                            Start Earning with Proxie
                                        </h2>
                                        <p className="text-zinc-500 text-lg mb-10 max-w-sm mx-auto leading-relaxed text-center">
                                            Join skilled professionals getting matched with local clients through AI.
                                        </p>

                                        <div className="space-y-4 mb-12 max-w-xs mx-auto text-left">
                                            {[
                                                'Get matched with local clients',
                                                'Set your own prices',
                                                'Work on your schedule'
                                            ].map((benefit, i) => (
                                                <div key={i} className="flex items-center text-zinc-300 font-bold text-sm">
                                                    <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mr-3 shrink-0">
                                                        <CheckCircle2 size={12} className="text-green-500" />
                                                    </div>
                                                    {benefit}
                                                </div>
                                            ))}
                                        </div>

                                        {enrollmentStatus === 'pending_verification' ? (
                                            <div className="bg-zinc-800/50 border border-zinc-700 rounded-2xl p-6 text-left">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <Clock className="text-amber-400" size={20} />
                                                    <span className="text-white font-black text-lg">Verification Pending</span>
                                                </div>
                                                <p className="text-zinc-500 text-sm">
                                                    We're reviewing your profile. This usually takes less than 24 hours.
                                                </p>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => handleSubmit("I want to become a provider")}
                                                className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-xl shadow-white/10"
                                            >
                                                Become a Provider
                                            </button>
                                        )}

                                        <p className="mt-8 text-zinc-600 text-sm font-bold text-center">
                                            Already enrolled? <button className="text-blue-500 underline ml-1">Sign In</button>
                                        </p>
                                    </div>
                                </div>
                            </section>
                        ) : (
                            <section>
                                <div className="flex items-center justify-between mb-3">
                                    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">New Leads</h2>
                                    <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full text-[10px] font-bold">
                                        {requests.length} Available
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    {requests.map((req) => (
                                        <div
                                            key={req.id}
                                            onClick={() => navigate(`/provider/request/${req.id}`)}
                                            className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 hover:border-green-800 hover:bg-zinc-900/80 transition-all cursor-pointer group"
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-[10px] font-black uppercase tracking-wider">
                                                    {req.service_type}
                                                </span>
                                                <span className="text-green-400 font-bold text-sm">
                                                    ${req.budget?.min || 50} - ${req.budget?.max || 100}
                                                </span>
                                            </div>
                                            <p className="text-zinc-300 text-sm italic mb-3">"{req.raw_input}"</p>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center text-xs text-zinc-500">
                                                    <MapPin size={12} className="mr-1" />
                                                    {req.location?.city || 'Brooklyn'}
                                                </div>
                                                <button className="flex items-center text-xs font-bold text-white bg-white/10 px-3 py-1.5 rounded-full group-hover:bg-green-600 transition-colors">
                                                    Make Offer <ArrowRight size={14} className="ml-1" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                    {requests.length === 0 && (
                                        <div className="text-center py-12 text-zinc-600">
                                            <Briefcase size={32} className="mx-auto mb-3" />
                                            <p className="font-medium">No leads right now</p>
                                            <p className="text-sm">Check back soon or ask Proxie</p>
                                        </div>
                                    )}
                                </div>
                            </section>
                        )}
                    </>
                )}
            </main>

            <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent pt-8">
                <div className="max-w-[480px] mx-auto">
                    {isVoiceMode && (
                        <div className="absolute inset-x-4 bottom-24 bg-zinc-900 border border-zinc-700 rounded-2xl p-6 text-center animate-pulse">
                            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mic size={32} className="text-red-500 animate-pulse" />
                            </div>
                            <p className="text-white font-bold mb-1">Listening...</p>
                            <p className="text-zinc-500 text-sm">Speak naturally, Proxie is ready</p>
                        </div>
                    )}

                    {selectedMedia.length > 0 && (
                        <div className="flex gap-2 mb-4 bg-zinc-900 shadow-xl p-3 rounded-2xl border border-zinc-800">
                            {selectedMedia.map((m) => (
                                <div key={m.id} className="relative group">
                                    <div className="w-16 h-16 rounded-lg bg-zinc-800 overflow-hidden border border-zinc-700">
                                        <img src={m.preview} alt="Preview" className="w-full h-full object-cover" />
                                    </div>
                                    <button onClick={() => removeMedia(m.id)} className="absolute -top-2 -right-2 bg-zinc-800 border border-zinc-700 text-zinc-400 p-1 rounded-full hover:text-white">
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="flex items-center space-x-3 relative">
                        {showAttachmentMenu && (
                            <div className="absolute bottom-full left-0 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl p-3 mb-2 flex flex-col gap-1 w-48 z-50">
                                <button onClick={() => { setShowCamera(true); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors">
                                    <Camera size={18} className="text-blue-400" />
                                    <span className="text-sm font-bold">Take Photo</span>
                                </button>
                                <button onClick={() => { fileInputRef.current.click(); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors">
                                    <Image size={18} className="text-green-400" />
                                    <span className="text-sm font-bold">Choose Photo</span>
                                </button>
                                <button onClick={() => { videoInputRef.current.click(); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors">
                                    <Video size={18} className="text-purple-400" />
                                    <span className="text-sm font-bold">Choose Video</span>
                                </button>
                            </div>
                        )}

                        <button onClick={() => setShowAttachmentMenu(!showAttachmentMenu)} className={`w-12 h-12 rounded-full flex items-center justify-center transition-all shrink-0 ${showAttachmentMenu ? 'bg-zinc-700 text-white' : 'bg-zinc-900 border border-zinc-700 text-zinc-400 hover:bg-zinc-800'}`}>
                            <Plus size={20} />
                        </button>

                        <div className="flex-1 flex items-center bg-zinc-800 rounded-full border border-zinc-700 pl-5 pr-2 py-2">
                            <input
                                type="text"
                                placeholder="Ask anything"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                                className="flex-1 bg-transparent border-none outline-none text-white placeholder-zinc-500 font-medium text-sm"
                            />
                            <div className="flex items-center space-x-1 ml-2">
                                <button onClick={() => { setIsListening(true); recognitionRef.current?.start(); }} className="p-2 rounded-full hover:bg-zinc-700 transition-colors">
                                    <Mic size={18} className={isListening ? 'text-red-500' : 'text-zinc-500'} />
                                </button>
                                <button onClick={toggleVoiceMode} className="w-9 h-9 bg-white rounded-full flex items-center justify-center hover:bg-zinc-200 transition-colors">
                                    <AudioWaveform size={18} className="text-black" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <p className="text-center text-zinc-600 text-[10px] mt-3 font-medium">
                        {activeTab === 'demand' ? 'Describe what you need' : 'Ask about new leads or manage your offers'}
                    </p>
                </div>
            </div>

            <input type="file" ref={fileInputRef} className="hidden" accept="image/*" multiple onChange={(e) => handleFileSelect(e, 'image')} />
            <input type="file" ref={videoInputRef} className="hidden" accept="video/*" onChange={(e) => handleFileSelect(e, 'video')} />

            {showCamera && (
                <CameraCapture onCapture={handleCameraCapture} onClose={() => setShowCamera(false)} />
            )}
        </div>
    );
};

export default DashboardPage;
