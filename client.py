import socket
import os
from dotenv import load_dotenv
import threading

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

def receive_messages(client):
    """Recibe y muestra mensajes del servidor"""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(f"\n📩 Mensaje recibido: {message}")  # DEBUG
            else:
                print("⚠️ Servidor cerró la conexión")
                break
        except:
            print("❌ Error recibiendo mensaje")
            client.close()
            break

def start_client():
    """Inicia el cliente con autenticación y registro."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("1. Iniciar sesión")
    print("2. Registrarse")
    choice = input("Selecciona una opción: ")

    client.send(choice.encode('utf-8'))

    if choice == "2":
        username = input("Elige un nombre de usuario: ")
        password = input("Elige una contraseña: ")

        client.send(username.encode('utf-8'))
        client.send(password.encode('utf-8'))

        response = client.recv(1024).decode('utf-8')
        if response == "REG_SUCCESS":
            print("✅ Registro exitoso. Ahora inicia sesión.")
        else:
            print("❌ El usuario ya existe.")
            client.close()
            return

    username = input("Usuario: ")
    password = input("Contraseña: ")

    client.send(username.encode('utf-8'))
    client.send(password.encode('utf-8'))

    response = client.recv(1024).decode('utf-8')
    if response == "SUCCESS":
        print("✅ Autenticado. Puedes empezar a chatear.")
        threading.Thread(target=receive_messages, args=(client,)).start()
    else:
        print("❌ Error en la autenticación.")
        client.close()
        return

    while True:
        message = input("Tú: ")
        print(f"📝 Enviando mensaje: {message}")  # DEBUG
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()
