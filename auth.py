import json
import bcrypt

USER_FILE = "users.json"

def load_users():
    """Carga los usuarios desde el archivo JSON."""
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    """Guarda los usuarios en el archivo JSON."""
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

def register_user(username, password):
    """Registra un nuevo usuario con contraseña hasheada."""
    users = load_users()
    if username in users:
        return False  # Usuario ya existe

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed_password
    save_users(users)
    return True

def authenticate_user(username, password):
    """Verifica si las credenciales son correctas."""
    users = load_users()
    if username in users:
        return bcrypt.checkpw(password.encode(), users[username].encode())
    return False
