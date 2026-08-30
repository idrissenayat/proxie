import { io } from 'socket.io-client';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let socket = null;

export function initSocket() {
    if (socket) {
        return socket;
    }

    socket = io(API_URL, {
        path: '/ws/socket.io',
        transports: ['websocket', 'polling'],
        autoConnect: true,
    });

    return socket;
}

export function getSocket() {
    return socket || initSocket();
}

export function joinChatSession(sessionId) {
    const current = getSocket();
    current.emit('join_session', { session_id: sessionId });
}

export function disconnectSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
}
