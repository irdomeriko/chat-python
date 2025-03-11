import socket
import threading
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

clients = []

def broadcast(message, sender):
    """Envía un mensaje a todos los clientes excepto el remitente"""
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client):
    """Maneja mensajes de cada cliente"""
    while True:
        try:
            message = client.recv(1024)
            broadcast(message, client)
        except:
            clients.remove(client)
            client.close()
            break

def start_server():
    """Inicia el servidor y espera conexiones"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Servidor escuchando en {HOST}:{PORT}...")

    while True:
        client, address = server.accept()
        print(f"Cliente conectado desde {address}")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_server()
