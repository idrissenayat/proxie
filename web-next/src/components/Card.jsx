import React from 'react';

const Card = ({ children, className = '' }) => {
    return (
        <div className={`bg-[#111827] rounded-2xl p-6 shadow-xl border border-gray-800 ${className}`}>
            {children}
        </div>
    );
};

export default Card;
