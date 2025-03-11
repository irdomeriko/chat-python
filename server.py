import socket
import threading
import os
from dotenv import load_dotenv
from auth import authenticate_user, register_user

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

clients = {}

def broadcast(message, sender):
    """Envía un mensaje a todos los clientes excepto el remitente."""
    print(f"🔹 Enviando mensaje: {message}")  # DEBUG
    for client in clients.values():
        if client != sender:
            try:
                client.send(message.encode('utf-8'))
                print("✅ Mensaje enviado a un cliente")  # DEBUG
            except:
                print("❌ Error enviando mensaje")  # DEBUG
                pass

def handle_client(client, username):
    """Maneja los mensajes de un cliente autenticado"""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"📨 Mensaje recibido de {username}: {message}")  # DEBUG
            broadcast(f"{username}: {message}", client)
        except:
            print(f"⚠️ Cliente {username} se desconectó inesperadamente.")
            break

    del clients[username]
    client.close()
    print(f"❌ {username} ha salido del chat.")

def start_server():
    """Inicia el servidor y espera conexiones"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"📡 Servidor escuchando en {HOST}:{PORT}...")

    while True:
        client, address = server.accept()
        print(f"✅ Cliente conectado desde {address}")

        choice = client.recv(1024).decode('utf-8')

        if choice == "2":  # Registro de usuario
            username = client.recv(1024).decode('utf-8')
            password = client.recv(1024).decode('utf-8')
            
            if register_user(username, password):
                client.send("REG_SUCCESS".encode('utf-8'))
            else:
                client.send("REG_FAIL".encode('utf-8'))
                client.close()
                continue

        username = client.recv(1024).decode('utf-8')
        password = client.recv(1024).decode('utf-8')

        if authenticate_user(username, password):
            client.send("SUCCESS".encode('utf-8'))
            clients[username] = client
            print(f"👥 Clientes conectados: {list(clients.keys())}")  # DEBUG
            thread = threading.Thread(target=handle_client, args=(client, username))
            thread.start()
        else:
            client.send("FAIL".encode('utf-8'))
            client.close()

if __name__ == "__main__":
    start_server()
