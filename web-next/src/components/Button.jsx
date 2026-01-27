import React from 'react';

const Button = ({ title, onClick, type = 'primary', loading = false, disabled = false, className = '' }) => {
    const baseStyle = "w-full py-3.5 rounded-xl font-semibold transition-opacity active:opacity-80 disabled:opacity-50 flex items-center justify-center cursor-pointer";
    const variants = {
        primary: "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-800 text-gray-100 hover:bg-gray-700",
        outline: "border-2 border-blue-600 text-blue-600 bg-transparent hover:bg-blue-600/10"
    };

    return (
        <button
            className={`${baseStyle} ${variants[type]} ${className}`}
            onClick={onClick}
            disabled={loading || disabled}
        >
            {loading ? (
                <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : title}
        </button>
    );
};

export default Button;
