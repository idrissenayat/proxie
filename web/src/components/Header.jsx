import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';

const Header = ({ title, showBack = false }) => {
    const navigate = useNavigate();

    return (
        <header className="flex items-center justify-between p-4 sticky top-0 bg-white/80 backdrop-blur-md z-10 border-b border-gray-100">
            <div className="w-10">
                {showBack && (
                    <button onClick={() => navigate(-1)} className="p-2 -ml-2 text-gray-600 hover:text-blue-600">
                        <ChevronLeft size={24} />
                    </button>
                )}
            </div>
            <h1 className="text-lg font-bold text-gray-900">{title}</h1>
            <div className="w-10" />
        </header>
    );
};

export default Header;
