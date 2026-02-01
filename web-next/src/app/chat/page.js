"use client";

import React, { useState, useEffect, useRef, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
    Send, Mic, MicOff, Star, MapPin,
    CheckCircle2, Calendar, Clock, DollarSign,
    ChevronLeft, Layout, Volume2, VolumeX, MessageCircle,
    Plus, Image, Video, Smartphone, Camera, X, Zap, ArrowRight, Sparkles, UserCircle
} from 'lucide-react';
import { useUser, UserButton, SignedIn } from '@clerk/nextjs';
import Header from '@/components/Header';
import Card from '@/components/Card';
import Button from '@/components/Button';
import CameraCapture from '@/components/CameraCapture';
import DraftRequestCard from '@/components/DraftRequestCard';
import UserProfileCard from '@/components/UserProfileCard';
import MediaViewer from '@/components/MediaViewer';
import ServiceSelector from '@/components/enrollment/ServiceSelector';
import PortfolioUploader from '@/components/enrollment/PortfolioUploader';
import EnrollmentSummaryCard from '@/components/enrollment/EnrollmentSummaryCard';
import { sendChatMessage, getServiceCatalog, startEnrollment } from '@/lib/api';
import { initSocket, getSocket, joinChatSession, disconnectSocket } from '@/lib/socket';

function ChatContent() {
    const { isLoaded, isSignedIn, user } = useUser();
    const router = useRouter();
    const searchParams = useSearchParams();
    const role = searchParams.get('role') || 'consumer';
    const providerId = searchParams.get('provider_id');
    const initialMessage = searchParams.get('initial');
    const rebookId = searchParams.get('rebook');
    const requestId = searchParams.get('request_id');

    const [messages, setMessages] = useState([]);
    const initialMessageAddedRef = useRef(false);
    const [input, setInput] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isVoiceOutputEnabled, setIsVoiceOutputEnabled] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const hasSentInitialRef = useRef(false);
    const [selectedMedia, setSelectedMedia] = useState([]);
    const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
    const [showCamera, setShowCamera] = useState(false);
    const [viewerState, setViewerState] = useState({ isOpen: false, media: [], index: 0 });
    const [serviceCatalog, setServiceCatalog] = useState([]);
    const [enrollmentData, setEnrollmentData] = useState(null);
    const [enrollmentId, setEnrollmentId] = useState(null);

    const fileInputRef = useRef(null);
    const videoInputRef = useRef(null);
    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);
    const processingRequestRef = useRef(null);

    // Add initial greeting message (only once, even with React Strict Mode)
    useEffect(() => {
        if (initialMessageAddedRef.current) return;
        
        const storageKey = `proxie_greeting_added_${role}`;
        if (typeof window !== 'undefined' && sessionStorage.getItem(storageKey)) {
            initialMessageAddedRef.current = true;
            return;
        }
        
        initialMessageAddedRef.current = true;
        if (typeof window !== 'undefined') {
            sessionStorage.setItem(storageKey, 'true');
        }
        
        const greeting = role === 'consumer'
            ? "Hi! I'm Proxie, your personal agent for finding skilled service providers. What can I help you with today?"
            : role === 'enrollment'
                ? "Hi! I'm Proxie. I'm ready to help you enroll as a provider. Let's start by getting to know you and your business!"
                : "Hi! I'm Proxie. I'm ready to help you manage your business. Would you like to see your new leads or manage active offers?";
        
        setMessages([{
            id: 'init',
            role: 'assistant',
            content: greeting
        }]);
    }, [role]);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isThinking]);

    // Socket.io initialization
    useEffect(() => {
        const socket = initSocket();

        const handleNewMessage = (data) => {
            console.log('Socket new_message received:', data.message?.substring(0, 50));
        };

        const handleSessionReady = (data) => {
            setSessionId(data.session_id);
        };

        socket.on('new_message', handleNewMessage);
        socket.on('session_ready', handleSessionReady);

        return () => {
            // Clean up socket listeners
            socket.off('new_message', handleNewMessage);
            socket.off('session_ready', handleSessionReady);
        };
    }, []);

    // Handle initial message and context
    useEffect(() => {
        // Prevent duplicate execution using both ref and sessionStorage (for React Strict Mode)
        const storageKey = `proxie_initial_sent_${role}_${initialMessage}_${rebookId}_${requestId}`;
        if (hasSentInitialRef.current || (typeof window !== 'undefined' && sessionStorage.getItem(storageKey))) {
            return;
        }

        const processInitial = async () => {
            // Double-check to prevent race conditions
            if (hasSentInitialRef.current || (typeof window !== 'undefined' && sessionStorage.getItem(storageKey))) {
                return;
            }
            hasSentInitialRef.current = true;
            if (typeof window !== 'undefined') {
                sessionStorage.setItem(storageKey, 'true');
            }

            if (role === 'enrollment') {
                try {
                    const res = await startEnrollment();
                    const id = res.data.enrollment_id;
                    setEnrollmentId(id);
                    if (typeof window !== 'undefined') {
                        localStorage.setItem('proxie_enrollment_id', id);
                    }
                    const catRes = await getServiceCatalog();
                    setServiceCatalog(catRes.data);

                    if (initialMessage) {
                        handleSend(initialMessage, null, id);
                    }
                } catch (e) {
                    console.error("Enrollment init error", e);
                    hasSentInitialRef.current = false;
                    if (typeof window !== 'undefined') {
                        sessionStorage.removeItem(storageKey);
                    }
                }
                return;
            }

            if (rebookId) {
                handleSend(`I want to rebook the previous service (Booking ID: ${rebookId})`);
                return;
            }

            if (requestId && role === 'provider') {
                handleSend(`Tell me about lead ${requestId}`);
                return;
            }

            if (initialMessage) {
                if (typeof window !== 'undefined') {
                    const savedMedia = sessionStorage.getItem('proxie_initial_media');
                    if (savedMedia) {
                        const media = JSON.parse(savedMedia);
                        setSelectedMedia(media);
                        sessionStorage.removeItem('proxie_initial_media');
                        setTimeout(() => handleSend(initialMessage, null, null, media), 100);
                        return;
                    }
                }
                handleSend(initialMessage);
            }
        };

        processInitial();
    }, [initialMessage, role, rebookId, requestId, handleSend]);

    // Speech Recognition Setup
    useEffect(() => {
        const SpeechRecognition = typeof window !== 'undefined' ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            
            let hasProcessedResult = false;
            
            const handleResult = (event) => {
                // Prevent duplicate processing
                if (hasProcessedResult) return;
                hasProcessedResult = true;
                
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                handleSend(transcript);
                setIsListening(false);
            };
            
            const handleError = () => {
                setIsListening(false);
                hasProcessedResult = false;
            };
            
            const handleEnd = () => {
                setIsListening(false);
                hasProcessedResult = false;
            };
            
            recognition.onresult = handleResult;
            recognition.onerror = handleError;
            recognition.onend = handleEnd;
            recognitionRef.current = recognition;
            
            return () => {
                // Clean up recognition
                if (recognitionRef.current) {
                    recognitionRef.current.onresult = null;
                    recognitionRef.current.onerror = null;
                    recognitionRef.current.onend = null;
                    try {
                        recognitionRef.current.stop();
                    } catch (e) {
                        // Ignore errors when stopping
                    }
                    recognitionRef.current = null;
                }
            };
        }
    }, [handleSend]);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            setInput('');
            setIsListening(true);
            recognitionRef.current?.start();
        }
    };

    const speak = (text) => {
        if (!isVoiceOutputEnabled) return;
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        synth.speak(utterance);
    };

    const handleSend = useCallback(async (customText = null, action = null, activeEnrollmentId = enrollmentId, initialMedia = null) => {
        // Prevent duplicate sends with multiple guards
        if (isThinking) {
            console.warn('Already processing a message, ignoring duplicate send');
            return;
        }

        const text = customText !== null ? customText : input;
        const mediaToUse = initialMedia || selectedMedia;

        if (!text.trim() && mediaToUse.length === 0 && !action) return;

        // Create a unique fingerprint for this request
        const requestFingerprint = `${text.substring(0, 50)}_${action || 'none'}_${mediaToUse.length}`;
        const requestKey = `proxie_request_${requestFingerprint}`;
        
        // Check if this exact request was already sent (within last 3 seconds)
        if (typeof window !== 'undefined') {
            const recentRequest = sessionStorage.getItem(requestKey);
            if (recentRequest) {
                const timeDiff = Date.now() - parseInt(recentRequest);
                if (timeDiff < 3000) { // Within 3 seconds
                    console.warn('Duplicate request detected (within 3s), ignoring', { text: text.substring(0, 30), timeDiff });
                    return;
                }
            }
            // Mark this request as sent
            sessionStorage.setItem(requestKey, Date.now().toString());
            // Clean up after 10 seconds
            setTimeout(() => sessionStorage.removeItem(requestKey), 10000);
        }

        // Also check processing ref
        if (processingRequestRef.current === requestFingerprint) {
            console.warn('Duplicate request in processing ref, ignoring');
            return;
        }
        processingRequestRef.current = requestFingerprint;

        // Set thinking state immediately to prevent duplicates
        setIsThinking(true);

        const mediaToUpload = mediaToUse.map(m => ({
            type: m.type,
            data: m.data,
            mime_type: m.mime_type
        }));

        const userMsg = {
            id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            role: 'user',
            content: text,
            media: mediaToUse.length > 0 ? [...mediaToUse] : null
        };

        const consumerId = typeof window !== 'undefined' ? localStorage.getItem('proxie_consumer_id') : null;

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setSelectedMedia([]);

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

            if (!sessionId && session_id) {
                setSessionId(session_id);
                joinChatSession(session_id);
            }

            const assistantMsg = {
                id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                role: 'assistant',
                content: message,
                data: data,
                draft: draft,
                awaiting_approval: awaiting_approval
            };

            setMessages(prev => [...prev, assistantMsg]);

            if (data?.enrollment_result?.status === 'verified') {
                const pid = data.enrollment_result.provider_id;
                if (typeof window !== 'undefined') {
                    localStorage.setItem('proxie_provider_id', pid);
                }
            }

            speak(message);
        } catch (err) {
            console.error("Chat error", err);
            setMessages(prev => [...prev, {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: "I'm sorry, I'm having trouble connecting. Please check your connection."
            }]);
        } finally {
            setIsThinking(false);
            // Clear processing ref after a delay to allow for rapid legitimate requests
            setTimeout(() => {
                if (processingRequestRef.current === requestFingerprint) {
                    processingRequestRef.current = null;
                }
            }, 1000);
        }
    }, [isThinking, input, selectedMedia, sessionId, role, providerId, enrollmentId]);

    const renderData = (data, draft, isUser) => {
        if (!data && !draft) return null;

        return (
            <div className="mt-4 space-y-3">
                {draft && (
                    <DraftRequestCard
                        data={draft}
                        onApprove={() => handleSend("Post Request", "approve_request")}
                        onEdit={() => handleSend(null, "edit_request")}
                    />
                )}
                {data?.consumer_profile && (
                    <UserProfileCard
                        profile={data.consumer_profile}
                        isAuthenticated={isSignedIn}
                    />
                )}
                {data?.categories && (
                    <ServiceSelector
                        categories={data.categories}
                        onSelect={(service) => handleSend(`I offer ${service.name}`, "select_service")}
                    />
                )}
                {data?.show_portfolio && (
                    <PortfolioUploader
                        onUpload={(urls) => handleSend(`I uploaded ${urls.length} photos`, "upload_portfolio")}
                    />
                )}
                {data?.enrollment_summary && (
                    <EnrollmentSummaryCard
                        summary={data.enrollment_summary}
                        onConfirm={() => handleSend("Submit Enrollment", "confirm_enrollment")}
                    />
                )}
                {data?.enrollment_result && (
                    <div className="bg-green-600/10 border border-green-500/20 p-4 rounded-xl text-green-400">
                        <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle2 size={18} />
                            <span className="font-bold uppercase tracking-widest text-xs">Enrollment Successful</span>
                        </div>
                        <p className="text-sm">Your profile has been submitted for verification. We'll notify you once it's active.</p>
                        <Button
                            variant="primary"
                            className="mt-4 w-full bg-green-600 border-none text-white hover:bg-green-500"
                            onClick={() => router.push('/')}
                        >
                            Return to Dashboard
                        </Button>
                    </div>
                )}
            </div>
        );
    };

    const handleFileSelect = (e, type) => {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (readerEvent) => {
                setSelectedMedia(prev => [...prev, {
                    id: Date.now() + Math.random(),
                    type: type,
                    data: readerEvent.target.result.split(",")[1],
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
            type: "image",
            data: dataUrl.split(",")[1],
            mime_type: "image/jpeg",
            preview: dataUrl
        }]);
    };

    const removeMedia = (id) => {
        setSelectedMedia(prev => prev.filter(m => m.id !== id));
    };

    const openViewer = (media, index) => {
        setViewerState({ isOpen: true, media, index });
    };

    return (
        <div className="flex flex-col h-screen bg-black overflow-hidden">
            <header className="flex items-center justify-between p-4 border-b border-zinc-800 bg-black/80 backdrop-blur-md z-10 shrink-0">
                <div className="flex items-center space-x-3">
                    <button onClick={() => router.back()} className="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors cursor-pointer">
                        <ChevronLeft size={24} />
                    </button>
                    <div>
                        <h1 className="text-sm font-black uppercase tracking-widest text-zinc-500">Concierge</h1>
                        <div className="flex items-center space-x-1.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                            <h2 className="text-white font-black tracking-tight italic">Proxie AI</h2>
                        </div>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button onClick={() => setIsVoiceOutputEnabled(!isVoiceOutputEnabled)} className={`p-2 rounded-xl transition-colors cursor-pointer ${isVoiceOutputEnabled ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20' : 'bg-zinc-900 text-zinc-500 border border-zinc-800 hover:text-white'}`}>
                        {isVoiceOutputEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                    </button>
                    <button className="p-2 bg-zinc-900 border border-zinc-800 text-zinc-500 rounded-xl hover:text-white cursor-pointer mr-1">
                        <Layout size={20} />
                    </button>
                    <SignedIn>
                        <UserButton
                            appearance={{
                                elements: {
                                    userButtonAvatarBox: "w-9 h-9 border border-zinc-800",
                                }
                            }}
                        />
                    </SignedIn>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide bg-black">
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
                                : 'bg-zinc-900 border border-zinc-800 text-zinc-100 rounded-bl-none'
                                }`}>
                                {msg.media && (
                                    <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
                                        {msg.media.map((m, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => openViewer(msg.media, idx)}
                                                className="w-20 h-20 rounded-lg bg-black/20 overflow-hidden shrink-0 border border-white/10 hover:border-white/30 transition-all cursor-pointer"
                                            >
                                                <img src={m.preview || m.url} alt="User upload" className="w-full h-full object-cover" />
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
                        <div className="w-8 h-8 bg-zinc-800 rounded-xl mr-2 flex items-center justify-center shrink-0 mt-1">
                            <span className="text-zinc-400 text-[10px] font-black">P</span>
                        </div>
                        <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-2xl rounded-bl-none flex items-center space-x-2">
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

            <div className="p-4 bg-black border-t border-zinc-800 shrink-0">
                {selectedMedia.length > 0 && (
                    <div className="flex gap-2 mb-4 bg-zinc-900 shadow-xl p-3 rounded-2xl border border-zinc-800">
                        {selectedMedia.map((m) => (
                            <div key={m.id} className="relative group">
                                <div className="w-16 h-16 rounded-lg bg-zinc-800 overflow-hidden border border-zinc-700">
                                    <img src={m.preview} alt="Preview" className="w-full h-full object-cover" />
                                </div>
                                <button onClick={() => removeMedia(m.id)} className="absolute -top-2 -right-2 bg-zinc-800 border border-zinc-700 text-zinc-400 p-1 rounded-full hover:text-white cursor-pointer">
                                    <X size={12} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex items-center space-x-3 relative">
                    {showAttachmentMenu && (
                        <div className="absolute bottom-full left-0 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl p-3 mb-2 flex flex-col gap-1 w-48 z-50 animate-in slide-in-from-bottom-2">
                            <button onClick={() => { setShowCamera(true); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors cursor-pointer">
                                <Camera size={18} className="text-blue-400" />
                                <span className="text-sm font-bold">Take Photo</span>
                            </button>
                            <button onClick={() => { fileInputRef.current.click(); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors cursor-pointer">
                                <Image size={18} className="text-green-400" />
                                <span className="text-sm font-bold">Choose Photo</span>
                            </button>
                            <button onClick={() => { videoInputRef.current.click(); setShowAttachmentMenu(false); }} className="flex items-center gap-3 p-3 text-zinc-300 hover:bg-zinc-800 rounded-xl transition-colors cursor-pointer">
                                <Video size={18} className="text-purple-400" />
                                <span className="text-sm font-bold">Choose Video</span>
                            </button>
                        </div>
                    )}

                    <button onClick={() => setShowAttachmentMenu(!showAttachmentMenu)} className={`w-12 h-12 rounded-full flex items-center justify-center transition-all shrink-0 cursor-pointer ${showAttachmentMenu ? 'bg-zinc-700 text-white' : 'bg-zinc-900 border border-zinc-700 text-zinc-400 hover:bg-zinc-800'}`}>
                        <Plus size={20} />
                    </button>

                    <div className="flex-1 flex items-center bg-zinc-900 rounded-full border border-zinc-800 pl-5 pr-2 py-2">
                        <input
                            type="text"
                            placeholder="Ask anything"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            className="flex-1 bg-transparent border-none outline-none text-white placeholder-zinc-500 font-medium text-sm !mb-0 !p-0"
                            disabled={isThinking}
                        />
                        <div className="flex items-center space-x-1 ml-2">
                            <button onClick={toggleListening} className={`p-2 rounded-full transition-colors cursor-pointer ${isListening ? 'bg-red-500/10 text-red-500' : 'text-zinc-500 hover:text-white'}`}>
                                {isListening ? <Mic size={18} className="animate-pulse" /> : <Mic size={18} />}
                            </button>
                            <button
                                onClick={() => handleSend()}
                                disabled={(!input.trim() && selectedMedia.length === 0) || isThinking}
                                className={`w-9 h-9 rounded-full flex items-center justify-center transition-all cursor-pointer ${((input.trim() || selectedMedia.length > 0) && !isThinking) ? 'bg-white text-black' : 'bg-zinc-800 text-zinc-600'}`}
                            >
                                <Send size={18} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <input type="file" ref={fileInputRef} className="hidden" accept="image/*" multiple onChange={(e) => handleFileSelect(e, 'image')} />
            <input type="file" ref={videoInputRef} className="hidden" accept="video/*" onChange={(e) => handleFileSelect(e, 'video')} />

            {showCamera && (
                <CameraCapture onCapture={handleCameraCapture} onClose={() => setShowCamera(false)} />
            )}

            {viewerState.isOpen && (
                <MediaViewer
                    media={viewerState.media}
                    index={viewerState.index}
                    onClose={() => setViewerState({ ...viewerState, isOpen: false })}
                    onPrev={() => setViewerState(prev => ({ ...prev, index: (prev.index - 1 + prev.media.length) % prev.media.length }))}
                    onNext={() => setViewerState(prev => ({ ...prev, index: (prev.index + 1) % prev.media.length }))}
                    isOpen={viewerState.isOpen}
                />
            )}
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={<div className="h-screen bg-black flex items-center justify-center text-zinc-500 font-bold uppercase tracking-widest animate-pulse">Initializing Chat...</div>}>
            <ChatContent />
        </Suspense>
    );
}
