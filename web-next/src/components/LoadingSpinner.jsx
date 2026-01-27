import React from 'react';

const LoadingSpinner = ({ fullPage = false }) => {
    const loader = (
        <div className="flex flex-col items-center justify-center p-8">
            <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-400 font-medium">Loading...</p>
        </div>
    );

    if (fullPage) {
        return (
            <div className="flex-1 flex items-center justify-center min-h-[60vh]">
                {loader}
            </div>
        );
    }

    return loader;
};

export default LoadingSpinner;
