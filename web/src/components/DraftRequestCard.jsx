import React from 'react';
import { CheckCircle2, Edit3, XCircle, MapPin, DollarSign, Calendar, Info } from 'lucide-react';
import Card from './Card';
import Button from './Button';

const DraftRequestCard = ({ draft, onApprove, onEdit, onCancel }) => {
    if (!draft) return null;

    return (
        <Card className="max-w-md bg-zinc-800 border-zinc-700 shadow-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="bg-zinc-700/50 p-3 flex items-center gap-2 border-b border-zinc-600">
                <CheckCircle2 className="w-5 h-5 text-blue-400" />
                <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Service Request Draft</h3>
            </div>

            <div className="p-4 space-y-4">
                <div>
                    <h4 className="text-xl font-bold text-white">{draft.service_type}</h4>
                    <p className="text-zinc-400 text-sm mt-1">{draft.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-2 text-zinc-300">
                        <div className="p-1.5 bg-zinc-700 rounded-lg">
                            <MapPin className="w-4 h-4 text-blue-400" />
                        </div>
                        <span className="text-xs font-medium">{draft.location?.city || 'Unknown'}</span>
                    </div>

                    <div className="flex items-center gap-2 text-zinc-300">
                        <div className="p-1.5 bg-zinc-700 rounded-lg">
                            <DollarSign className="w-4 h-4 text-green-400" />
                        </div>
                        <span className="text-xs font-medium">
                            {draft.budget ? `$${draft.budget.min} - $${draft.budget.max}` : 'Not specified'}
                        </span>
                    </div>

                    <div className="flex items-center gap-2 text-zinc-300">
                        <div className="p-1.5 bg-zinc-700 rounded-lg">
                            <Calendar className="w-4 h-4 text-purple-400" />
                        </div>
                        <span className="text-xs font-medium">{draft.timing || 'Flexible'}</span>
                    </div>
                </div>

                {draft.details && Object.keys(draft.details).length > 0 && (
                    <div className="bg-zinc-900/40 rounded-lg p-3 border border-zinc-700/50">
                        <h5 className="text-[10px] uppercase font-bold text-zinc-500 mb-2 flex items-center gap-1">
                            <Info className="w-3 h-3" /> Additional Details
                        </h5>
                        <ul className="space-y-1">
                            {Object.entries(draft.details).map(([key, value]) => {
                                // Skip complex objects or values that shouldn't be here
                                if (typeof value === 'object' && value !== null) return null;
                                return (
                                    <li key={key} className="text-xs text-zinc-300 flex justify-between">
                                        <span className="text-zinc-500 capitalize">{key.replace('_', ' ')}:</span>
                                        <span className="font-medium text-zinc-200">{String(value)}</span>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                )}

                {draft.media && draft.media.length > 0 && (
                    <div>
                        <h5 className="text-[10px] uppercase font-bold text-zinc-500 mb-2">Attached Media ({draft.media.length})</h5>
                        <div className="flex gap-2 overflow-x-auto pb-1">
                            {draft.media.map((item, idx) => (
                                <div key={idx} className="w-16 h-16 rounded-md bg-zinc-900 overflow-hidden flex-shrink-0 border border-zinc-700">
                                    {item.type === 'image' ? (
                                        <img src={item.url} alt="Draft" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-[10px] text-zinc-500">Video</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 pt-0 flex gap-2">
                <Button
                    onClick={onApprove}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white gap-2 h-10 text-sm"
                >
                    <CheckCircle2 className="w-4 h-4" /> Post Request
                </Button>
            </div>

            <div className="p-4 pt-0 flex gap-2">
                <Button
                    variant="secondary"
                    onClick={onEdit}
                    className="flex-1 bg-zinc-700 hover:bg-zinc-600 text-white gap-2 h-9 text-xs"
                >
                    <Edit3 className="w-4 h-4" /> Edit
                </Button>
                <Button
                    variant="secondary"
                    onClick={onCancel}
                    className="flex-1 bg-zinc-700 hover:bg-zinc-600 text-red-400 gap-2 h-9 text-xs"
                >
                    <XCircle className="w-4 h-4" /> Cancel
                </Button>
            </div>
        </Card>
    );
};

export default DraftRequestCard;
