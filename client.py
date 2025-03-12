import socket
import os
import threading
import curses
from dotenv import load_dotenv

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
                # 🔹 Evitar que el usuario vea su propio mensaje recibido del servidor
                if not message.startswith("Tú:"):  
                    messages.append(message)
                    stdscr.clear()
                    for i, msg in enumerate(messages[-15:]):  # Mostrar últimos 15 mensajes
                        stdscr.addstr(i, 0, msg)
                    stdscr.refresh()
            else:
                break
        except:
            break

def chat_ui(stdscr, client):
    """Interfaz de usuario con curses."""
    curses.curs_set(1)  # Mostrar cursor en la entrada
    stdscr.clear()
    stdscr.refresh()

    height, width = stdscr.getmaxyx()
    input_win = curses.newwin(1, width - 2, height - 2, 1)  # Ventana de entrada
    input_win.addstr(0, 0, "Escribe aquí: ")
    input_win.refresh()

    threading.Thread(target=receive_messages, args=(client, stdscr), daemon=True).start()

    while True:
        input_win.clear()
        input_win.addstr(0, 0, "Escribe aquí: ")
        input_win.refresh()
        curses.echo()
        message = input_win.getstr(0, 14).decode('utf-8')  # Leer mensaje del usuario

        if message.lower() == "/exit":
            client.close()
            break

        # 🔹 Guardar mensaje enviado en la lista de mensajes para mostrarlo en la UI
        messages.append(f"Tú: {message}")
        stdscr.clear()
        for i, msg in enumerate(messages[-15:]):  # Mostrar últimos 15 mensajes
            stdscr.addstr(i, 0, msg)
        stdscr.refresh()

        client.send(message.encode('utf-8'))

def start_client():
    """Inicia el cliente con autenticación y la UI."""
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
        print("✅ Autenticado. Iniciando chat...")
        input("Presiona ENTER para entrar en el chat...")  # Evita que curses limpie la terminal antes de ver el resultado
        curses.wrapper(chat_ui, client=client)  # ✅ Iniciar la UI de chat solo después de autenticarse
    else:
        print("❌ Error en la autenticación.")
        client.close()

if __name__ == "__main__":
    start_client()
