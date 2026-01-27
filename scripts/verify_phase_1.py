import requests
import asyncio
import socketio
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("--- Testing Liveness Probe ---")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"GET /health: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"FAILED: {e}")

def test_ready():
    print("\n--- Testing Readiness Probe ---")
    try:
        resp = requests.get(f"{BASE_URL}/ready")
        print(f"GET /ready: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"FAILED: {e}")

async def test_socket():
    print("\n--- Testing Socket.io ---")
    sio = socketio.AsyncClient()

    @sio.event
    async def connect():
        print("Connected to Socket.io!")

    @sio.event
    async def disconnect():
        print("Disconnected from Socket.io!")

    try:
        await sio.connect(f"{BASE_URL}", socketio_path="/ws/socket.io")
        await sio.emit("join_session", {"session_id": "test-session"})
        await sio.disconnect()
        print("Socket.io test complete!")
    except Exception as e:
        print(f"Socket.io test FAILED: {e}")

if __name__ == "__main__":
    test_health()
    test_ready()
    try:
        asyncio.run(test_socket())
    except KeyboardInterrupt:
        pass
