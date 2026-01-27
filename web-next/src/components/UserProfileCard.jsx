import React from 'react';
import { User, MapPin, Phone, Mail, Sparkles, LogIn } from 'lucide-react';
import Link from 'next/link';

const UserProfileCard = ({ profile, isAuthenticated = false, onSignUpClick }) => {
    if (!profile) return null;

    return (
        <div className="bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 p-6 border-b border-zinc-800 relative overflow-hidden">
                {/* Decorative background */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-[50px] rounded-full -mr-16 -mt-16" />

                <div className="flex items-center space-x-4 relative z-10">
                    <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center border border-zinc-700 shadow-lg shadow-blue-500/10">
                        {profile.profile_photo_url ? (
                            <img src={profile.profile_photo_url} alt={profile.name} className="w-full h-full object-cover rounded-2xl" />
                        ) : (
                            <User size={32} className="text-white" />
                        )}
                    </div>
                    <div>
                        <h3 className="text-xl font-black text-white tracking-tight">{profile.name || "New Client"}</h3>
                        <div className="flex items-center space-x-1 mt-1">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Active Profile</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-6 space-y-4">
                {profile.default_location && (
                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center border border-zinc-700 mt-0.5">
                            <MapPin size={14} className="text-blue-400" />
                        </div>
                        <div>
                            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Default Location</p>
                            <p className="text-sm font-bold text-white leading-snug">
                                {profile.default_location.address || profile.default_location.city || "Not set"}
                            </p>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                    {profile.phone && (
                        <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center border border-zinc-700 mt-0.5">
                                <Phone size={14} className="text-emerald-400" />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Phone</p>
                                <p className="text-sm font-bold text-white">{profile.phone}</p>
                            </div>
                        </div>
                    )}
                    {profile.email && (
                        <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center border border-zinc-700 mt-0.5">
                                <Mail size={14} className="text-purple-400" />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Email</p>
                                <p className="text-sm font-bold text-white truncate w-24">{profile.email}</p>
                            </div>
                        </div>
                    )}
                </div>

                {!isAuthenticated && (
                    <div className="mt-6 pt-6 border-t border-zinc-800">
                        <div className="bg-blue-600/10 border border-blue-500/20 rounded-2xl p-4 mb-4">
                            <div className="flex items-center space-x-2 mb-2">
                                <Sparkles size={14} className="text-blue-400" />
                                <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Unsaved Data</span>
                            </div>
                            <p className="text-xs text-zinc-400 font-medium leading-relaxed">
                                Connect your account to save your profile and preferences for future concierge requests.
                            </p>
                        </div>
                        <Link
                            href="/sign-up"
                            className="w-full h-12 bg-white text-black rounded-xl font-black text-sm flex items-center justify-center space-x-2 active:scale-95 transition-all shadow-xl shadow-white/5"
                        >
                            <LogIn size={16} />
                            <span>Connect Now</span>
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UserProfileCard;
