import React from 'react';
import {
    User, Briefcase, MapPin, Clock,
    Camera, FileText, CheckCircle2
} from 'lucide-react';

const EnrollmentSummaryCard = ({ data, onEdit, onSubmit }) => {
    return (
        <div className="bg-zinc-900 border border-zinc-700/50 rounded-[2.5rem] overflow-hidden w-full max-w-md animate-in fade-in slide-in-from-bottom-6 duration-700 shadow-2xl">
            <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 p-8 border-b border-zinc-800 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-zinc-100/5 blur-3xl rounded-full -mr-16 -mt-16" />
                <h2 className="text-2xl font-black text-white mb-1">Review Enrollment</h2>
                <p className="text-zinc-500 text-xs font-bold uppercase tracking-widest">Master Profile</p>
            </div>

            <div className="p-8 space-y-8 max-h-[60vh] overflow-y-auto custom-scrollbar">
                {/* Profile Section */}
                <section>
                    <div className="flex items-center text-zinc-500 mb-4 sticky top-0 bg-zinc-900 py-1 z-10">
                        <User size={16} className="mr-2" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Personal Info</span>
                    </div>
                    <div className="space-y-1 pl-6 border-l border-zinc-800">
                        <p className="text-white font-bold">{data.full_name || 'Anonymous'}</p>
                        <p className="text-zinc-500 text-sm">{data.email}</p>
                        <p className="text-zinc-500 text-sm">{data.phone}</p>
                    </div>
                </section>

                {/* Services Section */}
                <section>
                    <div className="flex items-center text-zinc-500 mb-4 sticky top-0 bg-zinc-900 py-1 z-10">
                        <Briefcase size={16} className="mr-2" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Services & Pricing</span>
                    </div>
                    <div className="space-y-4 pl-6 border-l border-zinc-800">
                        {data.services?.map((svc, i) => (
                            <div key={i} className="bg-zinc-800/30 rounded-2xl p-4 border border-zinc-800">
                                <p className="text-white font-black text-sm">{svc.name}</p>
                                <p className="text-zinc-400 text-xs mt-1">
                                    ${svc.price_min}-{svc.price_max} • {svc.duration_min}-{svc.duration_max} min
                                </p>
                                {svc.specializations?.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2">
                                        {svc.specializations.map((spec, j) => (
                                            <span key={j} className="px-2 py-0.5 bg-zinc-800 text-zinc-500 rounded text-[9px] font-bold uppercase">
                                                {spec}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </section>

                {/* Location Section */}
                <section>
                    <div className="flex items-center text-zinc-500 mb-4 sticky top-0 bg-zinc-900 py-1 z-10">
                        <MapPin size={16} className="mr-2" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Location</span>
                    </div>
                    <div className="pl-6 border-l border-zinc-800">
                        <p className="text-white font-bold text-sm">
                            {data.location?.address}
                        </p>
                        <p className="text-zinc-500 text-xs">
                            {data.location?.city}, {data.location?.radius} mile radius
                        </p>
                    </div>
                </section>

                {/* Portfolio Section */}
                {data.portfolio?.length > 0 && (
                    <section>
                        <div className="flex items-center text-zinc-500 mb-4 sticky top-0 bg-zinc-900 py-1 z-10">
                            <Camera size={16} className="mr-2" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Portfolio</span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 pl-6 border-l border-zinc-800">
                            {data.portfolio.slice(0, 6).map((img, i) => (
                                <div key={i} className="aspect-square bg-zinc-800 rounded-xl overflow-hidden border border-zinc-700">
                                    <img src={img.preview || img.url} alt="" className="w-full h-full object-cover" />
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </div>

            <div className="p-8 bg-zinc-900 border-t border-zinc-800 flex flex-col gap-3">
                <button
                    onClick={onSubmit}
                    className="w-full h-14 bg-white text-black rounded-2xl font-black text-sm flex items-center justify-center hover:scale-[1.02] active:scale-95 transition-all shadow-xl shadow-white/5"
                >
                    <CheckCircle2 size={18} className="mr-2" />
                    Submit Enrollment
                </button>
                <button
                    onClick={onEdit}
                    className="w-full h-14 bg-zinc-800 text-white rounded-2xl font-black text-sm flex items-center justify-center hover:bg-zinc-700 active:scale-95 transition-all border border-zinc-700"
                >
                    <FileText size={18} className="mr-2" />
                    Edit Something
                </button>
            </div>
        </div>
    );
};

export default EnrollmentSummaryCard;
