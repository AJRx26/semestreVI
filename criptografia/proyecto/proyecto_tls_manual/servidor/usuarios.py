# registrar_usuario.py
import utils
import getpass

usuario = input("Usuario: ")
password = getpass.getpass("Contraseña: ")

salt = utils.generar_salt()
hash_pw = utils.hashear_password(password, salt)

with open("usuarios.txt", "a") as f:
    f.write(f"{usuario}:{salt}:{hash_pw}\n")

print(f"Usuario '{usuario}' registrado.")