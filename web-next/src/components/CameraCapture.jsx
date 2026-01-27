"use client";

import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Camera, X, RefreshCcw, Check } from 'lucide-react';
import Button from './Button';

const CameraCapture = ({ onCapture, onClose }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [capturedImage, setCapturedImage] = useState(null);
    const [error, setError] = useState(null);

    const startCamera = useCallback(async () => {
        try {
            const constraints = {
                video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
            };
            const newStream = await navigator.mediaDevices.getUserMedia(constraints);
            setStream(newStream);
            if (videoRef.current) {
                videoRef.current.srcObject = newStream;
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            setError("Unable to access camera. Please check permissions.");
        }
    }, []);

    useEffect(() => {
        startCamera();
        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [startCamera]);

    const capture = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL('image/jpeg');
            setCapturedImage(dataUrl);

            // Stop the stream once captured
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                setStream(null);
            }
        }
    };

    const retake = () => {
        setCapturedImage(null);
        startCamera();
    };

    const confirm = () => {
        onCapture(capturedImage);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center">
            <div className="relative w-full max-w-lg aspect-[3/4] bg-zinc-900 overflow-hidden shadow-2xl">
                {error ? (
                    <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
                        <X className="w-12 h-12 text-red-500 mb-4" />
                        <p className="text-white mb-6">{error}</p>
                        <Button type="secondary" onClick={onClose} title="Close" />
                    </div>
                ) : capturedImage ? (
                    <img src={capturedImage} alt="Captured" className="w-full h-full object-cover" />
                ) : (
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        className="w-full h-full object-cover"
                    />
                )}

                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 bg-black/50 rounded-full text-white hover:bg-black/80 transition-colors cursor-pointer"
                >
                    <X className="w-6 h-6" />
                </button>
            </div>

            <div className="mt-8 flex items-center gap-6">
                {!capturedImage ? (
                    <button
                        onClick={capture}
                        className="w-16 h-16 bg-white rounded-full flex items-center justify-center hover:scale-105 active:scale-95 transition-transform cursor-pointer"
                    >
                        <div className="w-14 h-14 border-2 border-black rounded-full" />
                    </button>
                ) : (
                    <>
                        <button
                            onClick={retake}
                            className="p-4 bg-zinc-800 rounded-full text-white hover:bg-zinc-700 transition-colors cursor-pointer"
                        >
                            <RefreshCcw className="w-6 h-6" />
                        </button>
                        <button
                            onClick={confirm}
                            className="p-4 bg-blue-600 rounded-full text-white hover:bg-blue-500 transition-colors cursor-pointer"
                        >
                            <Check className="w-6 h-6" />
                        </button>
                    </>
                )}
            </div>

            <canvas ref={canvasRef} className="hidden" />
        </div>
    );
};

export default CameraCapture;
