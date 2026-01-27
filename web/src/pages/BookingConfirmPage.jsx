import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Button from '../components/Button';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import { CheckCircle2, Calendar, Clock, DollarSign, User } from 'lucide-react';

const BookingConfirmPage = () => {
    const { id } = useParams(); // offer ID
    const navigate = useNavigate();

    return (
        <div className="flex flex-col min-h-screen bg-gray-50">
            <Header title="Confirmed!" />

            <main className="p-4 flex-1 flex flex-col justify-center items-center">
                <div className="mb-8 flex flex-col items-center">
                    <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-6">
                        <CheckCircle2 size={60} className="text-green-600" />
                    </div>
                    <h2 className="text-3xl font-black text-gray-900 text-center leading-tight">Booking Confirmed!</h2>
                    <p className="text-gray-500 text-center mt-2">Your pro is notified and ready to go.</p>
                </div>

                <Card className="w-full mb-8 border-2 border-green-500 shadow-lg shadow-green-100">
                    <div className="space-y-6">
                        <div className="flex items-center space-x-4">
                            <div className="p-3 bg-gray-100 rounded-xl text-gray-600"><User size={20} /></div>
                            <div>
                                <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Provider</p>
                                <p className="font-bold text-gray-800">Verified Pro</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-gray-100 rounded-xl text-gray-600"><Clock size={20} /></div>
                                <div>
                                    <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Time</p>
                                    <p className="font-bold text-gray-800">2:00 PM</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-gray-100 rounded-xl text-gray-600"><DollarSign size={20} /></div>
                                <div>
                                    <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Price</p>
                                    <p className="font-bold text-gray-800">$60.00</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </Card>

                <Button title="Back to Home" type="secondary" onClick={() => navigate('/')} />
            </main>
        </div>
    );
};

export default BookingConfirmPage;
