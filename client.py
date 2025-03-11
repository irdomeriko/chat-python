import socket
import threading
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

def receive_messages(client):
    """Recibe y muestra mensajes del servidor"""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print("\n" + message)
        except:
            print("Conexión cerrada.")
            client.close()
            break

def start_client():
    """Inicia el cliente y permite enviar mensajes"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        message = input("Tú: ")
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()
