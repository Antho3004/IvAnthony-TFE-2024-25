import secrets
secret_key = secrets.token_hex(32)  # Génère une clé secrète hexadécimale de 64 caractères
print(secret_key)
