import socket
import os
import threading
import curses
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    filename="client.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cargar variables de entorno
load_dotenv()

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 12345))

# Lista de mensajes para la UI
messages = []

def receive_messages(client, stdscr):
    """Recibe y muestra mensajes en la UI de curses."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                if not message.startswith("Tú:"):  
                    messages.append(message)
                    stdscr.clear()
                    for i, msg in enumerate(messages[-15:]):  
                        stdscr.addstr(i, 0, msg)
                    stdscr.refresh()
                    logging.info(f"Mensaje recibido: {message}")
            else:
                break
        except:
            logging.error("Error recibiendo mensajes", exc_info=True)
            break

def chat_ui(stdscr, client):
    """Interfaz de usuario con curses."""
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

    height, width = stdscr.getmaxyx()
    input_win = curses.newwin(1, width - 2, height - 2, 1)
    input_win.addstr(0, 0, "Escribe aquí: ")
    input_win.refresh()

    threading.Thread(target=receive_messages, args=(client, stdscr), daemon=True).start()

    while True:
        input_win.clear()
        input_win.addstr(0, 0, "Escribe aquí: ")
        input_win.refresh()
        curses.echo()
        message = input_win.getstr(0, 14).decode('utf-8')

        if message.lower() == "/exit":
            client.close()
            logging.info("Cliente desconectado")
            break

        messages.append(f"Tú: {message}")
        stdscr.clear()
        for i, msg in enumerate(messages[-15:]):
            stdscr.addstr(i, 0, msg)
        stdscr.refresh()

        client.send(message.encode('utf-8'))
        logging.info(f"Mensaje enviado: {message}")

def start_client():
    """Inicia el cliente con autenticación y la UI."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    logging.info("Cliente conectado al servidor")

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
            logging.info(f"Usuario {username} registrado correctamente")
        else:
            logging.warning(f"Error al registrar usuario {username}")
            client.close()
            return

    username = input("Usuario: ")
    password = input("Contraseña: ")

    client.send(username.encode('utf-8'))
    client.send(password.encode('utf-8'))

    response = client.recv(1024).decode('utf-8')

    if response == "SUCCESS":
        logging.info(f"Usuario {username} autenticado")
        curses.wrapper(chat_ui, client=client)
    else:
        logging.warning(f"Intento de inicio de sesión fallido para {username}")
        client.close()

if __name__ == "__main__":
    start_client()
