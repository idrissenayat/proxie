import React from 'react';

const Button = ({ title, onClick, type = 'primary', loading = false, disabled = false, className = '' }) => {
    const baseStyle = "w-full py-3.5 rounded-xl font-semibold transition-opacity active:opacity-80 disabled:opacity-50 flex items-center justify-center";
    const variants = {
        primary: "bg-blue-600 text-white",
        secondary: "bg-gray-200 text-gray-800",
        outline: "border-2 border-blue-600 text-blue-600 bg-transparent"
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
