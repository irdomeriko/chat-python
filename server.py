import socket
import threading
import os
import logging
from dotenv import load_dotenv
from auth import authenticate_user, register_user

# Crear carpeta de logs si no existe
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configurar logging para el servidor
logging.basicConfig(
    filename="logs/server.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

clients = {}

def broadcast(message, sender):
    """Envía un mensaje a todos los clientes EXCEPTO al remitente."""
    logging.info(f"Enviando mensaje: {message}")
    print(f"INFO: Enviando mensaje: {message}")
    for client in clients.values():
        if client != sender:
            try:
                client.send(message.encode('utf-8'))
                logging.info(f"Mensaje enviado a {client}")
                print(f"INFO: Mensaje enviado a {client}")
            except:
                logging.error("Error enviando mensaje", exc_info=True)
                print("ERROR: Error enviando mensaje")
                pass

def handle_client(client, username):
    """Maneja los mensajes de un cliente autenticado"""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            logging.info(f"Mensaje recibido de {username}: {message}")
            print(f"INFO: Mensaje recibido de {username}: {message}")
            broadcast(f"{username}: {message}", client)
        except:
            logging.error(f"Error con el cliente {username}", exc_info=True)
            print(f"ERROR: Error con el cliente {username}")
            break

    del clients[username]
    client.close()
    logging.info(f"{username} ha salido del chat.")
    print(f"INFO: {username} ha salido del chat.")

def start_server():
    """Inicia el servidor y espera conexiones"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Servidor escuchando en {HOST}:{PORT}")
    print(f"INFO: Servidor escuchando en {HOST}:{PORT}")

    while True:
        client, address = server.accept()
        logging.info(f"Cliente conectado desde {address}")
        print(f"INFO: Cliente conectado desde {address}")

        choice = client.recv(1024).decode('utf-8')

        if choice == "2":
            username = client.recv(1024).decode('utf-8')
            password = client.recv(1024).decode('utf-8')
            
            if register_user(username, password):
                client.send("REG_SUCCESS".encode('utf-8'))
                logging.info(f"Usuario {username} registrado exitosamente.")
                print(f"INFO: Usuario {username} registrado exitosamente.")
            else:
                client.send("REG_FAIL".encode('utf-8'))
                logging.warning(f"Intento de registro fallido para {username}")
                print(f"WARNING: Intento de registro fallido para {username}")
                client.close()
                continue

        username = client.recv(1024).decode('utf-8')
        password = client.recv(1024).decode('utf-8')

        if authenticate_user(username, password):
            client.send("SUCCESS".encode('utf-8'))
            clients[username] = client
            logging.info(f"Usuario {username} autenticado y conectado.")
            print(f"INFO: Usuario {username} autenticado y conectado.")
            thread = threading.Thread(target=handle_client, args=(client, username))
            thread.start()
        else:
            client.send("FAIL".encode('utf-8'))
            logging.warning(f"Intento de inicio de sesión fallido para {username}")
            print(f"WARNING: Intento de inicio de sesión fallido para {username}")
            client.close()

if __name__ == "__main__":
    start_server()
