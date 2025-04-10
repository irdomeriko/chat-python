import os
print("""
Escribe un número para elegir una opción:
1. Servidor
2. Cliente 
3. Salir
""")
respuesta = int(input())

if respuesta == 1:
    os.system("python3 server.py")
elif respuesta == 2:
    os.system("python3 client.py")
elif respuesta ==3:
    exit()
else:
    print("Opción no válida")
    exit()