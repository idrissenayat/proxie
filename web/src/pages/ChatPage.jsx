import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import {
    Send, Mic, MicOff, Star, MapPin,
    CheckCircle2, Calendar, Clock, DollarSign,
    ChevronLeft, Layout, Volume2, VolumeX, MessageCircle,
    Plus, Image, Video, Smartphone, Camera, X
} from 'lucide-react';
import Header from '../components/Header';
import Card from '../components/Card';
import Button from '../components/Button';
import CameraCapture from '../components/CameraCapture';
import DraftRequestCard from '../components/DraftRequestCard';
import MediaViewer from '../components/MediaViewer';
import ServiceSelector from '../components/enrollment/ServiceSelector';
import PortfolioUploader from '../components/enrollment/PortfolioUploader';
import EnrollmentSummaryCard from '../components/enrollment/EnrollmentSummaryCard';
import { sendChatMessage, getServiceCatalog, startEnrollment, updateEnrollment, submitEnrollment } from '../api/client';

const ChatPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const query = new URLSearchParams(location.search);
    const role = query.get('role') || 'consumer';
    const providerId = query.get('provider_id') || location.state?.providerId;
    const initialMessage = query.get('initial');

    const [messages, setMessages] = useState([
        {
            id: 'init',
            role: 'assistant',
            content: role === 'consumer'
                ? "Hi! I'm Proxie, your personal agent for finding skilled service providers. What can I help you with today?"
                : "Hi! I'm Proxie. I'm ready to help you manage your business. Would you like to see your new leads or manage active offers?"
        }
    ]);
    const [input, setInput] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isVoiceOutputEnabled, setIsVoiceOutputEnabled] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [hasSentInitial, setHasSentInitial] = useState(false);
    const [selectedMedia, setSelectedMedia] = useState([]);
    const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
    const [showCamera, setShowCamera] = useState(false);
    const [pendingAction, setPendingAction] = useState(null);
    const [viewerState, setViewerState] = useState({ isOpen: false, media: [], index: 0 });
    const [serviceCatalog, setServiceCatalog] = useState([]);
    const [enrollmentData, setEnrollmentData] = useState(null);
    const [enrollmentId, setEnrollmentId] = useState(null);

    const fileInputRef = useRef(null);
    const videoInputRef = useRef(null);

    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Handle initial message from URL or state (contextual leads/edits)
    useEffect(() => {
        const targetLead = location.state?.targetLead;
        const editRequest = location.state?.edit_request;
        const bookProvider = location.state?.book_provider;

        if (targetLead && !hasSentInitial && role === 'provider') {
            setHasSentInitial(true);
            const contextMsg = `Tell me about lead ${targetLead}`;
            setTimeout(() => handleSend(contextMsg), 500);
            return;
        }

        if (editRequest && !hasSentInitial) {
            setHasSentInitial(true);
            const contextMsg = `I want to edit my request for ${editRequest.service_type}. Here are the current details: ${editRequest.raw_input}`;
            setTimeout(() => handleSend(contextMsg), 500);
            return;
        }

        if (bookProvider && !hasSentInitial) {
            setHasSentInitial(true);
            const contextMsg = `I want to book ${bookProvider.name} for ${bookProvider.specializations?.[0] || 'service'}`;
            setTimeout(() => handleSend(contextMsg), 500);
            return;
        }

        if (initialMessage && !hasSentInitial) {
            setHasSentInitial(true);

            // Handle enrollment initialization
            if (role === 'enrollment') {
                startEnrollment().then(res => {
                    const id = res.data.enrollment_id;
                    setEnrollmentId(id);
                    localStorage.setItem('proxie_enrollment_id', id);
                    getServiceCatalog().then(catRes => setServiceCatalog(catRes.data));
                    handleSend(initialMessage, null, id);
                });
                return;
            }

            // Check for initial media from dashboard
            const savedMedia = sessionStorage.getItem('proxie_initial_media');
            if (savedMedia) {
                const media = JSON.parse(savedMedia);
                setSelectedMedia(media);
                sessionStorage.removeItem('proxie_initial_media');
                setTimeout(() => handleSend(initialMessage), 500);
            } else {
                setTimeout(() => handleSend(initialMessage), 500);
            }
        }
    }, [initialMessage, hasSentInitial, location.state]);

    // Speech Recognition Setup
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.interimResults = false;

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                handleSend(transcript);
                setIsListening(false);
            };

            recognition.onerror = () => setIsListening(false);
            recognition.onend = () => setIsListening(false);

            recognitionRef.current = recognition;
        }
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            setIsListening(true);
            recognitionRef.current?.start();
        }
    };

    const handleFileSelect = (e, type) => {
        const files = Array.from(e.target.files);
        if (files.length + selectedMedia.length > 5) {
            alert("Maximum 5 attachments allowed");
            return;
        }

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

    const openViewer = (media, index) => {
        setViewerState({ isOpen: true, media, index });
    };

    const speak = (text) => {
        if (!isVoiceOutputEnabled) return;
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    };

    const handleSend = async (overrideInput, action = null, providedEnrollmentId = null) => {
        const text = overrideInput || input;
        const activeEnrollmentId = providedEnrollmentId || enrollmentId;
        if (!text.trim() && selectedMedia.length === 0 && !action) return;

        const mediaToUpload = selectedMedia.map(m => ({
            type: m.type,
            data: m.data,
            mime_type: m.mime_type
        }));

        const userMsg = {
            id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            role: 'user',
            content: text,
            media: selectedMedia.length > 0 ? [...selectedMedia] : null
        };

        const consumerId = localStorage.getItem('proxie_consumer_id');
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setSelectedMedia([]);
        setIsThinking(true);

        try {
            const response = await sendChatMessage({
                message: text,
                session_id: sessionId,
                role: role,
                consumer_id: consumerId,
                provider_id: providerId,
                enrollment_id: activeEnrollmentId,
                media: mediaToUpload.length > 0 ? mediaToUpload : null,
                action: action
            });

            const { message, session_id, data, draft, awaiting_approval } = response.data;
            setSessionId(session_id);

            const assistantMsg = {
                id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                role: 'assistant',
                content: message,
                data: data,
                draft: draft,
                awaiting_approval: awaiting_approval
            };

            setMessages(prev => [...prev, assistantMsg]);

            // Handle enrollment success
            if (data?.enrollment_result?.status === 'verified') {
                const pid = data.enrollment_result.provider_id;
                localStorage.setItem('proxie_provider_id', pid);
                setIsProviderEnrolled?.(true); // If we pass this setter from context or parent
            }

            speak(message);
        } catch (err) {
            setMessages(prev => [...prev, {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: "I'm sorry, I'm having trouble connecting. Please check your connection."
            }]);
        } finally {
            setIsThinking(false);
        }
    };

    const renderData = (data, draft, isUser) => {
        if (!data && !draft) return null;

        return (
            <div className="mt-4 space-y-3">
                {/* Draft Request Card */}
                {draft && (
                    <DraftRequestCard
                        draft={draft}
                        onApprove={() => handleSend("Post Request", "approve_request")}
                        onEdit={() => handleSend(null, "edit_request")}
                        onCancel={() => handleSend(null, "cancel_request")}
                    />
                )}
                {/* Provider Cards */}
                {data.offers?.map((offer) => (
                    <div key={offer.id} className="bg-zinc-900 border border-zinc-700 rounded-xl p-4 hover:border-blue-500/50 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <div className="font-bold text-white">{offer.provider_snapshot?.name || offer.service_name}</div>
                                <div className="flex items-center text-amber-400 text-xs font-bold">
                                    <Star size={12} fill="currentColor" className="mr-1" />
                                    {offer.provider_snapshot?.rating || '5.0'} ({offer.provider_snapshot?.review_count || '24'})
                                </div>
                            </div>
                            <div className="text-xl font-black text-green-400">${offer.price}</div>
                        </div>
                        <div className="text-xs text-zinc-500 mb-3 flex items-center">
                            <Clock size={12} className="mr-1" /> {offer.available_slots ? offer.available_slots[0].date : 'Today'} @ {offer.available_slots ? offer.available_slots[0].start_time : '2pm'}
                        </div>
                        <button
                            onClick={() => handleSend(`Book ${offer.provider_snapshot?.name || 'this pro'}`)}
                            className="w-full py-2 bg-white text-black font-bold rounded-lg text-sm hover:bg-zinc-200 transition-colors"
                        >
                            Book Now
                        </button>
                    </div>
                ))}

                {/* Booking Confirmation Card */}
                {data.booking && (
                    <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                        <div className="flex items-center space-x-3 mb-3">
                            <CheckCircle2 className="text-green-400" size={24} />
                            <div className="font-bold text-green-400 text-lg">Booking Confirmed!</div>
                        </div>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between"><span className="text-green-600">Provider</span><span className="font-bold text-white">{data.booking.provider_name}</span></div>
                            <div className="flex justify-between"><span className="text-green-600">Time</span><span className="font-bold text-white">{data.booking.date} @ {data.booking.time}</span></div>
                            <div className="flex justify-between border-t border-green-500/30 pt-2 mt-2"><span className="text-green-500 font-bold">Total</span><span className="font-black text-green-400">${data.booking.price}</span></div>
                        </div>
                    </div>
                )}

                {/* Lead Cards for Providers */}
                {data.requests?.map((req) => (
                    <div key={req.request_id} className="bg-zinc-900 border border-zinc-700 rounded-xl p-4">
                        <div className="flex justify-between items-center mb-2">
                            <span className="bg-blue-500/20 text-blue-400 text-[10px] font-black px-2 py-0.5 rounded uppercase leading-none">{req.service_type}</span>
                            <span className="text-green-400 font-bold text-xs">${req.budget?.min}-${req.budget?.max}</span>
                        </div>
                        <p className="text-zinc-300 text-sm mb-3 italic">"{req.raw_input}"</p>
                        <div className="flex items-center text-xs text-zinc-500 mb-3">
                            <MapPin size={12} className="mr-1" /> {req.location?.city}
                        </div>
                        <button
                            onClick={() => handleSend(`I want to make an offer for the ${req.service_type} in ${req.location?.city}`)}
                            className="w-full py-2 bg-zinc-800 text-white font-bold rounded-lg text-sm hover:bg-zinc-700 transition-colors border border-zinc-600"
                        >
                            Make Offer
                        </button>
                    </div>
                ))}

                {/* AI Offer Suggestion */}
                {data.suggestion && (
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-5 relative overflow-hidden group">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center shrink-0">
                                <Sparkles size={20} className="text-blue-400" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-[10px] font-black tracking-widest uppercase text-blue-400 mb-1">AI Suggestion</h3>
                                <p className="text-xs text-zinc-400 mb-3 leading-relaxed">{data.suggestion.reasoning}</p>
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="px-3 py-1 bg-zinc-800 rounded-lg text-xs font-bold text-zinc-300 border border-zinc-700">Rec: ${data.suggestion.suggested_price.recommended}</div>
                                    <div className="px-3 py-1 bg-zinc-800 rounded-lg text-xs font-bold text-zinc-300 border border-zinc-700">Dur: {data.suggestion.suggested_duration}m</div>
                                </div>
                                <button
                                    onClick={() => handleSend(`Draft an offer for $${data.suggestion.suggested_price.recommended}`)}
                                    className="w-full py-2.5 bg-blue-500 text-white font-black rounded-xl text-xs hover:bg-blue-600 transition-all flex items-center justify-center gap-2"
                                >
                                    Draft This Offer <ArrowRight size={14} />
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Offer Draft for Provider Approval */}
                {data.offer_draft && (
                    <div className="bg-zinc-900 border-2 border-zinc-800 rounded-3xl p-6 shadow-2xl overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-3 opacity-10">
                            <Zap size={64} className="text-white" />
                        </div>
                        <h3 className="text-xs font-black tracking-widest uppercase text-zinc-500 mb-4 border-b border-zinc-800 pb-2">📤 Offer Draft</h3>
                        <div className="space-y-4 mb-6">
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1">Offered Price</p>
                                    <p className="text-3xl font-black text-green-400">${data.offer_draft.price}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1">Proposed Timing</p>
                                    <p className="text-sm font-bold text-white">{data.offer_draft.date} @ {data.offer_draft.time}</p>
                                </div>
                            </div>
                            <div className="bg-black/20 rounded-2xl p-4 border border-zinc-800/50">
                                <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mb-1">Your Message</p>
                                <p className="text-xs text-zinc-300 italic leading-relaxed">"{data.offer_draft.message}"</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleSend("Send this offer", "submit_offer")}
                                className="flex-[2] py-3.5 bg-white text-black font-black rounded-2xl text-sm hover:bg-zinc-200 active:scale-95 transition-all shadow-xl shadow-white/5"
                            >
                                Send Offer
                            </button>
                            <button
                                onClick={() => handleSend("Let me edit the message")}
                                className="flex-1 py-3.5 bg-zinc-800 text-zinc-400 font-bold rounded-2xl text-sm hover:bg-zinc-700 transition-all"
                            >
                                Edit
                            </button>
                        </div>
                    </div>
                )}

                {/* Enrollment Catalog Selector */}
                {data.categories && (
                    <div className="mt-4">
                        <ServiceSelector
                            catalog={data.categories}
                            selectedServices={enrollmentData?.services || []}
                            onSelect={(services) => {
                                setEnrollmentData(prev => ({ ...prev, services }));
                                // Inform the agent
                                handleSend(`I've selected these services: ${services.map(s => s.name).join(', ')}`, null);
                            }}
                        />
                    </div>
                )}

                {/* Enrollment Portfolio Uploader */}
                {data.show_portfolio && (
                    <div className="mt-4">
                        <PortfolioUploader
                            photos={enrollmentData?.portfolio || []}
                            onAdd={(photo) => {
                                setEnrollmentData(prev => ({
                                    ...prev,
                                    portfolio: [...(prev?.portfolio || []), photo]
                                }));
                                setSelectedMedia(prev => [...prev, {
                                    id: photo.id,
                                    type: 'image',
                                    data: photo.preview.split(',')[1],
                                    mime_type: 'image/jpeg',
                                    preview: photo.preview
                                }]);
                            }}
                            onRemove={(id) => {
                                setEnrollmentData(prev => ({
                                    ...prev,
                                    portfolio: prev.portfolio.filter(p => p.id !== id)
                                }));
                                setSelectedMedia(prev => prev.filter(m => m.id !== id));
                            }}
                        />
                        <div className="mt-3 flex justify-center">
                            <button
                                onClick={() => handleSend("I've finished uploading my portfolio", null)}
                                className="bg-zinc-800 text-white px-6 h-10 rounded-full font-bold text-xs"
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}

                {/* Enrollment Summary */}
                {data.enrollment_summary && (
                    <div className="mt-4">
                        <EnrollmentSummaryCard
                            data={data.enrollment_summary}
                            onEdit={() => handleSend("I need to edit something in my enrollment")}
                            onSubmit={() => handleSend("I approve and submit my enrollment", "submit_enrollment")}
                        />
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="flex flex-col h-screen bg-zinc-950">
            {/* Header */}
            <header className="flex items-center justify-between p-4 border-b border-zinc-800 bg-zinc-950/90 backdrop-blur-md z-10">
                <div className="flex items-center space-x-2">
                    <button onClick={() => navigate('/')} className="p-2 -ml-2 text-zinc-500 hover:text-white">
                        <ChevronLeft size={24} />
                    </button>
                    <div>
                        <h1 className="text-lg font-black text-white leading-tight">Agent Proxie</h1>
                        <div className="flex items-center text-[10px] text-green-500 font-bold uppercase tracking-widest">
                            <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1 animate-pulse" /> Online
                        </div>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setIsVoiceOutputEnabled(!isVoiceOutputEnabled)}
                        className={`p-2 rounded-xl transition-colors ${isVoiceOutputEnabled ? 'bg-blue-500/20 text-blue-400' : 'text-zinc-500'}`}
                    >
                        {isVoiceOutputEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                    </button>
                    <Link to={role === 'consumer' ? '/request/new' : '/provider'} className="flex items-center space-x-1 px-3 py-1.5 bg-zinc-800 text-zinc-400 rounded-xl text-xs font-bold hover:bg-zinc-700 transition-colors border border-zinc-700">
                        <Layout size={14} />
                        <span>FORMS</span>
                    </Link>
                </div>
            </header>

            {/* Chat Messages */}
            <main className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide bg-zinc-950">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl mr-2 flex items-center justify-center shrink-0 mt-1 shadow-lg">
                                <span className="text-white text-[10px] font-black">P</span>
                            </div>
                        )}
                        <div className="max-w-[85%]">
                            <div className={`p-4 rounded-2xl ${msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-br-none font-medium text-sm'
                                : 'bg-zinc-800 border border-zinc-700 text-zinc-100 rounded-bl-none'
                                }`}>
                                {msg.media && (
                                    <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
                                        {msg.media.map((m, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => openViewer(msg.media, idx)}
                                                className="w-20 h-20 rounded-lg bg-black/20 overflow-hidden shrink-0 border border-white/10 hover:border-white/30 transition-all"
                                            >
                                                {m.type === 'image' ? (
                                                    <img src={m.preview} alt="User upload" className="w-full h-full object-cover" />
                                                ) : (
                                                    <div className="w-full h-full flex items-center justify-center text-[10px] text-white/50">Video</div>
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                )}
                                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                                {msg.role === 'assistant' && renderData(msg.data, msg.draft, false)}
                            </div>
                        </div>
                    </div>
                ))}

                {isThinking && (
                    <div className="flex justify-start">
                        <div className="w-8 h-8 bg-zinc-700 rounded-xl mr-2 flex items-center justify-center shrink-0 mt-1">
                            <span className="text-zinc-400 text-[10px] font-black">P</span>
                        </div>
                        <div className="bg-zinc-800 border border-zinc-700 p-4 rounded-2xl rounded-bl-none flex items-center space-x-2">
                            <div className="flex space-x-1">
                                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" />
                            </div>
                            <span className="text-xs text-zinc-400 font-bold uppercase tracking-widest italic animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </main>

            {/* Bottom Input */}
            <div className="p-4 bg-zinc-950 border-t border-zinc-800 relative">
                {/* Media Preview Strip */}
                {selectedMedia.length > 0 && (
                    <div className="flex gap-2 mb-4 bg-zinc-900/50 p-3 rounded-2xl border border-zinc-800 animate-in fade-in slide-in-from-bottom-2">
                        {selectedMedia.map((m) => (
                            <div key={m.id} className="relative group">
                                <div className="w-16 h-16 rounded-lg bg-zinc-800 overflow-hidden border border-zinc-700">
                                    {m.type === 'image' ? (
                                        <img src={m.preview} alt="Preview" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-[10px] text-zinc-500">Video</div>
                                    )}
                                </div>
                                <button
                                    onClick={() => removeMedia(m.id)}
                                    className="absolute -top-2 -right-2 bg-zinc-800 border border-zinc-700 text-zinc-400 p-1 rounded-full hover:text-white"
                                >
                                    <X size={12} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Attachment Menu */}
                {showAttachmentMenu && (
                    <div className="absolute bottom-full left-4 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl p-3 mb-2 flex flex-col gap-1 w-48 animate-in fade-in zoom-in-95 slide-in-from-bottom-2 duration-200">
                        <button
                            onClick={() => setShowCamera(true)}
                            className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors"
                        >
                            <Camera size={18} className="text-blue-400" />
                            <span className="text-sm font-bold">Take Photo</span>
                        </button>
                        <button
                            onClick={() => fileInputRef.current.click()}
                            className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors"
                        >
                            <Image size={18} className="text-green-400" />
                            <span className="text-sm font-bold">Choose Photo</span>
                        </button>
                        <button
                            onClick={() => videoInputRef.current.click()}
                            className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors"
                        >
                            <Video size={18} className="text-purple-400" />
                            <span className="text-sm font-bold">Choose Video</span>
                        </button>
                    </div>
                )}

                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="image/*"
                    multiple
                    onChange={(e) => handleFileSelect(e, 'image')}
                />
                <input
                    type="file"
                    ref={videoInputRef}
                    className="hidden"
                    accept="video/*"
                    onChange={(e) => handleFileSelect(e, 'video')}
                />

                {isListening && (
                    <div className="flex items-center justify-center mb-3 animate-pulse">
                        <div className="bg-red-500/20 text-red-400 px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest flex items-center border border-red-500/30">
                            <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-ping" />
                            Listening...
                        </div>
                    </div>
                )}
                <div className="flex items-center space-x-3 bg-zinc-800 p-2 rounded-full border border-zinc-700 focus-within:border-zinc-600 transition-colors">
                    <button
                        onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
                        className={`p-3 rounded-full transition-all ${showAttachmentMenu ? 'bg-zinc-700 text-white' : 'text-zinc-500 hover:text-white'}`}
                    >
                        <Plus size={20} />
                    </button>
                    <input
                        className="flex-1 bg-transparent border-none outline-none py-2 px-1 text-white placeholder-zinc-500 font-medium text-sm"
                        placeholder="Ask anything"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        disabled={isThinking}
                    />
                    <button
                        onClick={toggleListening}
                        className={`p-2 rounded-full transition-all ${isListening ? 'bg-red-500 text-white' : 'text-zinc-500 hover:text-white'}`}
                    >
                        {isListening ? <MicOff size={18} /> : <Mic size={18} />}
                    </button>
                    <button
                        onClick={() => handleSend()}
                        disabled={(!input.trim() && selectedMedia.length === 0) || isThinking}
                        className={`p-3 rounded-full transition-all ${((input.trim() || selectedMedia.length > 0) && !isThinking) ? 'bg-white text-black' : 'bg-zinc-700 text-zinc-500'}`}
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>

            {showCamera && (
                <CameraCapture
                    onCapture={handleCameraCapture}
                    onClose={() => setShowCamera(false)}
                />
            )}

            {viewerState.isOpen && (
                <MediaViewer
                    media={viewerState.media}
                    currentIndex={viewerState.index}
                    onClose={() => setViewerState({ ...viewerState, isOpen: false })}
                    onNavigate={(index) => setViewerState({ ...viewerState, index })}
                />
            )}

            {/* Bottom Nav Fallback */}
            <nav className="flex items-center border-t border-zinc-800 bg-zinc-950">
                <button className="flex-1 py-4 flex flex-col items-center text-white border-t-2 border-white">
                    <MessageCircle size={20} />
                    <span className="text-[10px] font-bold uppercase mt-1">Chat</span>
                </button>
                <button
                    onClick={() => navigate(role === 'consumer' ? '/request/new' : '/provider')}
                    className="flex-1 py-4 flex flex-col items-center text-zinc-600"
                >
                    <Layout size={20} />
                    <span className="text-[10px] font-bold uppercase mt-1">Forms</span>
                </button>
            </nav>
        </div>
    );
};

export default ChatPage;
