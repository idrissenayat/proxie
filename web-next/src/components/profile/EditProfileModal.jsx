"use client";

import React, { useState } from 'react';
import { X, Camera, Save, User, Briefcase, Phone, Book, Award } from 'lucide-react';

const EditProfileModal = ({ provider, onClose, onSave }) => {
    const [formData, setFormData] = useState({
        name: provider.name || '',
        business_name: provider.business_name || '',
        bio: provider.bio || '',
        phone: provider.phone || '',
        years_experience: provider.years_experience || 0,
        profile_photo_url: provider.profile_photo_url || ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-md">
            <div className="bg-black border-t sm:border border-white/10 rounded-t-[3rem] sm:rounded-[3rem] w-full max-w-lg overflow-hidden animate-in slide-in-from-bottom duration-500 shadow-2xl">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <h2 className="text-xl font-black text-white">Edit Profile</h2>
                    <button onClick={onClose} className="p-2 bg-zinc-900 rounded-full text-zinc-500 cursor-pointer"><X size={20} /></button>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-6 max-h-[70vh] overflow-y-auto">
                    {/* Photo */}
                    <div className="flex flex-col items-center mb-8">
                        <div className="relative w-24 h-24 bg-zinc-900 rounded-[2rem] border-2 border-white/5 overflow-hidden mb-3">
                            {formData.profile_photo_url ? (
                                <img src={formData.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-zinc-700"><Camera size={32} /></div>
                            )}
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity cursor-pointer">
                                <Camera size={20} className="text-white" />
                            </div>
                        </div>
                        <input
                            name="profile_photo_url"
                            value={formData.profile_photo_url}
                            onChange={handleChange}
                            placeholder="Photo URL"
                            className="bg-transparent border-none outline-none text-[10px] text-center text-zinc-500 font-bold uppercase tracking-widest w-full"
                        />
                    </div>

                    <div className="space-y-4">
                        <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-4">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-2">Display Name</label>
                            <div className="flex items-center gap-3">
                                <User size={18} className="text-zinc-600" />
                                <input
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="bg-transparent border-none outline-none text-white font-bold w-full"
                                    placeholder="Your Name"
                                />
                            </div>
                        </div>

                        <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-4">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-2">Business Name</label>
                            <div className="flex items-center gap-3">
                                <Briefcase size={18} className="text-zinc-600" />
                                <input
                                    name="business_name"
                                    value={formData.business_name}
                                    onChange={handleChange}
                                    className="bg-transparent border-none outline-none text-white font-bold w-full"
                                    placeholder="Your Business / Brand"
                                />
                            </div>
                        </div>

                        <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-4">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-2">Years of Experience</label>
                            <div className="flex items-center gap-3">
                                <Award size={18} className="text-zinc-600" />
                                <input
                                    type="number"
                                    name="years_experience"
                                    value={formData.years_experience}
                                    onChange={handleChange}
                                    className="bg-transparent border-none outline-none text-white font-bold w-full"
                                    placeholder="0"
                                />
                            </div>
                        </div>

                        <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-4">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-2">Professional Bio</label>
                            <div className="flex items-start gap-3">
                                <Book size={18} className="text-zinc-600 mt-1" />
                                <textarea
                                    name="bio"
                                    value={formData.bio}
                                    onChange={handleChange}
                                    rows={4}
                                    className="bg-transparent border-none outline-none text-white font-medium text-sm w-full resize-none"
                                    placeholder="Tell clients about your craft..."
                                />
                            </div>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full h-16 bg-white text-black rounded-2xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-white/10 mt-8 cursor-pointer"
                    >
                        <Save size={20} /> Save Profile
                    </button>
                </form>
            </div>
        </div>
    );
};

export default EditProfileModal;
