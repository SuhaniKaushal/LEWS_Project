from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

KEY = b'ThisIsA16ByteKey'  # Must be exactly 16, 24, or 32 bytes

def encrypt_message(message: str) -> str:
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(iv + ciphertext).decode()

def decrypt_message(enc_message: str) -> str:
    raw = base64.b64decode(enc_message)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()
