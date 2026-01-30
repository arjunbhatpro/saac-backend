import os
import base64
import hashlib
import random
import string
import time
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# ================= ENV SECRET =================
SECRET = os.getenv("SECRET_KEY")

if not SECRET:
    raise ValueError("SECRET_KEY not found in .env")

# ================= ORDER ID =================
def generate_order_id():
    return "SAAC" + ''.join(random.choices(string.digits, k=6))

# ================= ENCRYPTION KEY =================
def generate_key():
    return base64.urlsafe_b64encode(
        hashlib.sha256(SECRET.encode()).digest()
    )

fernet = Fernet(generate_key())

# ================= ENCRYPT / DECRYPT =================
def encrypt_data(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt_data(text):
    return fernet.decrypt(text.encode()).decode()

# ================= TOKEN STORAGE =================
TOKENS = {}

# ================= TOKEN GENERATOR =================
def generate_token(order_id, expiry_seconds=600):
    token = secrets.token_urlsafe(24)

    TOKENS[token] = {
        "order": order_id,
        "expiry": time.time() + expiry_seconds
    }

    return token

# ================= TOKEN VERIFIER =================
def verify_token(token, order_id):
    data = TOKENS.get(token)

    if not data:
        return False

    if data["order"] != order_id:
        return False

    if time.time() > data["expiry"]:
        TOKENS.pop(token, None)
        return False

    return True
