import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Button from '../components/Button';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import { getRequest, getOffersForRequest, acceptOffer } from '../api/client';
import { RefreshCw, Star, MapPin } from 'lucide-react';

const OffersPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [request, setRequest] = useState(null);
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [acceptingId, setAcceptingId] = useState(null);

    const fetchData = async () => {
        try {
            const [reqRes, offRes] = await Promise.all([
                getRequest(id),
                getOffersForRequest(id)
            ]);
            setRequest(reqRes.data);
            setOffers(offRes.data);
        } catch (error) {
            console.error("Error fetching offers:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [id]);

    const handleAccept = async (offer) => {
        setAcceptingId(offer.id);
        try {
            await acceptOffer(offer.id, {
                status: "accepted",
                confirmed_slot: offer.available_slots[0] // Default to first slot
            });
            navigate(`/booking/${offer.id}`);
        } catch (error) {
            alert("Failed to accept offer.");
        } finally {
            setAcceptingId(null);
        }
    };

    if (loading && !request) return <LoadingSpinner fullPage />;

    return (
        <div className="flex flex-col min-h-screen bg-gray-50">
            <Header title="Your Offers" showBack />

            <main className="p-4 space-y-4">
                {request && (
                    <Card className="bg-blue-600 text-white border-none mb-6">
                        <h2 className="text-xl font-bold mb-1">{request.service_type}</h2>
                        <p className="opacity-90 flex items-center text-sm">
                            <MapPin size={14} className="mr-1" /> {request.location?.city}
                        </p>
                        <div className="mt-3 text-sm bg-white/10 p-2 rounded-lg italic">
                            "{request.raw_input}"
                        </div>
                    </Card>
                )}

                <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold text-gray-700">{offers.length} Offers Found</h3>
                    <button onClick={fetchData} className="p-2 text-blue-600 hover:bg-blue-50 rounded-full transition-colors">
                        <RefreshCw size={20} />
                    </button>
                </div>

                {offers.length === 0 ? (
                    <div className="py-20 text-center">
                        <LoadingSpinner />
                        <p className="text-gray-400 mt-4 px-10">We're notifying matching providers. Offers usually appear in 30-60s.</p>
                    </div>
                ) : (
                    <div className="space-y-4 pb-20">
                        {offers.map(offer => (
                            <Card key={offer.id} className="relative overflow-hidden">
                                <div className="flex justify-between items-start mb-4">
                                    <div
                                        className="cursor-pointer group/provider"
                                        onClick={() => navigate(`/providers/${offer.provider_id}`)}
                                    >
                                        <h4 className="font-bold text-lg text-gray-900 group-hover/provider:text-blue-600 transition-colors">
                                            {offer.provider_snapshot?.name || offer.service_name}
                                        </h4>
                                        <div className="flex items-center text-amber-500 text-sm font-medium">
                                            <Star size={14} fill="currentColor" className="mr-1" /> {offer.provider_snapshot?.rating || '5.0'} ({offer.provider_snapshot?.review_count || '0'} reviews)
                                        </div>
                                        <div className="text-[10px] font-black text-blue-500 uppercase tracking-widest mt-1 group-hover/provider:underline">
                                            View Profile
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-2xl font-black text-blue-600">${offer.price}</div>
                                        <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">Fixed Price</div>
                                    </div>
                                </div>

                                <div className="mb-4 bg-gray-50 p-3 rounded-xl text-sm text-gray-600 border border-gray-100">
                                    {offer.message}
                                </div>

                                <div className="flex items-center space-x-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
                                    {offer.available_slots?.map((slot, i) => (
                                        <div key={i} className="bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap border border-blue-100 italic">
                                            {slot.date} @ {slot.start_time}
                                        </div>
                                    ))}
                                </div>

                                <Button
                                    title="Accept Offer"
                                    onClick={() => handleAccept(offer)}
                                    loading={acceptingId === offer.id}
                                />
                            </Card>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default OffersPage;
