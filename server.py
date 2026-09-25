# server.py - Updated for RSA support
import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 12345

clients = {}  # username → socket

def broadcast_user_list():
    """Send user list to everyone"""
    user_list = list(clients.keys())
    packet = json.dumps({"type": "user_list", "users": user_list}) + "\n"
    for sock in clients.values():
        try:
            sock.send(packet.encode('utf-8'))
        except:
            pass

def handle_client(conn, addr):
    username = None
    buffer = ""

    try:
        while True:
            # Increased buffer size for RSA
            data = conn.recv(65536).decode('utf-8')
            if not data:
                break
            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if line.startswith("USER:"):
                    username = line[5:].strip()
                    if username in clients:
                        conn.send("TAKEN\n".encode())
                        conn.close()
                        return
                    clients[username] = conn
                    print(f"[+] {username} connected ({addr})")
                    broadcast_user_list()

                else:
                    # Handle all other messages
                    try:
                        packet = json.loads(line)
                        if packet.get("to") in clients:
                            target_sock = clients[packet["to"]]
                            target_sock.send((line + "\n").encode('utf-8'))
                            if packet["type"] == "message":
                                msg_preview = packet['cipher'][:60] if len(packet['cipher']) <= 60 else packet['cipher'][:60] + "..."
                                print(f"[MSG] {packet['from']} → {packet['to']}: {msg_preview}")
                    except Exception as e:
                        print(f"[ERROR] Failed to process packet: {e}")

    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    finally:
        if username and username in clients:
            del clients[username]
            print(f"[-] {username} disconnected")
            broadcast_user_list()
        conn.close()

# Start server
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"Secure Messenger Server started on {HOST}:{PORT}")
print(f"Supports RSA encryption with large key exchange")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()