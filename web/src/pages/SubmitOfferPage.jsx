import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    MessageSquare, Calendar, Clock, DollarSign,
    Sparkles, ArrowRight, ChevronLeft, Check,
    Zap, AlertCircle
} from 'lucide-react';
import { submitOffer, sendChatMessage } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const SubmitOfferPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [initialLoading, setInitialLoading] = useState(true);
    const [suggestion, setSuggestion] = useState(null);

    const requestId = location.state?.requestId;
    const providerId = location.state?.providerId;

    const [form, setForm] = useState({
        price: '',
        date: '2026-01-30',
        startTime: '14:00',
        endTime: '15:00',
        message: ''
    });

    useEffect(() => {
        const fetchSuggestion = async () => {
            if (!requestId || !providerId) {
                setInitialLoading(false);
                return;
            }
            try {
                // Get AI suggestion via chat session (provider role)
                // In a real app we'd have a specific endpoint for this, 
                // but let's use the chat service with 'suggest_offer' tool logic
                // For MVP, we'll simulate the tool call result
                const res = await sendChatMessage({
                    message: "Give me an offer suggestion for this lead",
                    role: "provider",
                    provider_id: providerId,
                    session_id: `suggestion-${requestId}`
                });

                if (res.data.data?.suggestion) {
                    setSuggestion(res.data.data.suggestion);
                    setForm(prev => ({
                        ...prev,
                        price: res.data.data.suggestion.suggested_price.recommended,
                        message: res.data.data.suggestion.suggested_message
                    }));
                }
            } catch (error) {
                console.error("Error fetching suggestion:", error);
            } finally {
                setInitialLoading(false);
            }
        };
        fetchSuggestion();
    }, [requestId, providerId]);

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                request_id: requestId,
                provider_id: providerId,
                price: parseFloat(form.price),
                message: form.message,
                available_slots: [
                    {
                        date: form.date,
                        start_time: form.startTime,
                        end_time: form.endTime
                    }
                ]
            };
            await submitOffer(payload);
            navigate('/provider', { state: { offerSubmitted: true } });
        } catch (error) {
            console.error(error);
            alert("Failed to submit offer.");
        } finally {
            setLoading(false);
        }
    };

    if (initialLoading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><LoadingSpinner /></div>;
    if (!requestId) return <div className="min-h-screen bg-zinc-950 p-8 text-center text-red-500 font-bold">Missing request data</div>;

    const useSlot = (slot) => {
        setForm({ ...form, date: slot.date, startTime: slot.time });
    };

    return (
        <div className="flex flex-col min-h-screen bg-zinc-950 text-white pb-10">
            {/* Header */}
            <header className="p-4 pt-6 bg-zinc-950 sticky top-0 z-40 border-b border-zinc-900">
                <div className="flex items-center gap-4">
                    <button onClick={() => navigate(-1)} className="text-zinc-500"><ChevronLeft /></button>
                    <h1 className="text-xl font-black">Make an Offer</h1>
                </div>
            </header>

            <main className="p-5 max-w-2xl mx-auto w-full space-y-8">
                {/* AI Suggestion Banner */}
                {suggestion && (
                    <section className="bg-blue-500/10 border border-blue-500/20 rounded-3xl p-5 relative overflow-hidden">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center shrink-0">
                                <Sparkles size={20} className="text-blue-400" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-blue-400 uppercase tracking-widest mb-1">AI Suggestion Applied</h3>
                                <p className="text-xs text-zinc-400 leading-relaxed mb-3">
                                    {suggestion.reasoning}
                                </p>
                                <div className="flex items-center gap-2">
                                    <div className="px-3 py-1.5 bg-zinc-900 rounded-lg text-xs font-bold text-zinc-300">
                                        Price: ${suggestion.suggested_price.recommended}
                                    </div>
                                    <div className="px-3 py-1.5 bg-zinc-900 rounded-lg text-xs font-bold text-zinc-300">
                                        Dur: {suggestion.suggested_duration}m
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                )}

                <div className="space-y-6">
                    {/* Price Input */}
                    <div>
                        <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 block px-1">Your Price ($)</label>
                        <div className="relative group">
                            <DollarSign size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-white transition-colors" />
                            <input
                                type="number"
                                step="0.01"
                                className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl h-14 pl-12 pr-4 font-black text-xl outline-none focus:border-white transition-all text-white placeholder-zinc-700"
                                placeholder="0.00"
                                value={form.price}
                                onChange={(e) => setForm({ ...form, price: e.target.value })}
                            />
                        </div>
                    </div>

                    {/* Time Slots */}
                    <div>
                        <div className="flex items-center justify-between mb-3 px-1">
                            <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Available Slots</label>
                            <span className="text-[10px] text-zinc-600 font-bold flex items-center gap-1"><Zap size={10} /> Smart Suggestions</span>
                        </div>

                        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                            {suggestion?.available_slots?.map((slot, i) => (
                                <button
                                    key={i}
                                    type="button"
                                    onClick={() => useSlot(slot)}
                                    className={`flex flex-col items-center gap-1 px-4 py-3 rounded-2xl border transition-all whitespace-nowrap min-w-[100px] ${form.date === slot.date && form.startTime === slot.time
                                            ? 'bg-white border-white text-black'
                                            : 'bg-zinc-900 border-zinc-800 text-zinc-400'
                                        }`}
                                >
                                    <span className="text-[10px] font-black uppercase">{new Date(slot.date).toLocaleDateString('en-US', { weekday: 'short' })}</span>
                                    <span className="text-sm font-black">{slot.time}</span>
                                </button>
                            ))}
                        </div>

                        <div className="grid grid-cols-2 gap-3 mt-3">
                            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-3">
                                <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Custom Date</span>
                                <input
                                    type="date"
                                    className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                                    value={form.date}
                                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                                />
                            </div>
                            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-3">
                                <span className="text-[10px] font-bold text-zinc-600 uppercase block mb-1">Start Time</span>
                                <input
                                    type="time"
                                    className="bg-transparent border-none outline-none text-white text-sm font-bold w-full"
                                    value={form.startTime}
                                    onChange={(e) => setForm({ ...form, startTime: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Message */}
                    <div>
                        <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2 block px-1">Pitch to Consumer</label>
                        <textarea
                            className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl p-4 h-32 outline-none focus:border-white transition-all text-white placeholder-zinc-700 text-sm leading-relaxed"
                            placeholder="Tell them why you're a good fit..."
                            value={form.message}
                            onChange={(e) => setForm({ ...form, message: e.target.value })}
                        />
                    </div>
                </div>
            </main>

            {/* Submit Button */}
            <div className="p-5 mt-auto">
                <button
                    onClick={handleSubmit}
                    disabled={loading || !form.price}
                    className="w-full bg-white text-black h-16 rounded-2xl font-black flex items-center justify-center gap-3 disabled:opacity-50 active:scale-95 transition-all shadow-xl shadow-white/5"
                >
                    {loading ? <LoadingSpinner size="sm" color="zinc-900" /> : (
                        <>Submit Your Offer <ArrowRight size={20} /></>
                    )}
                </button>
            </div>
        </div>
    );
};

export default SubmitOfferPage;
