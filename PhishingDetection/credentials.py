from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
key = bytes.fromhex(os.getenv('ENCRYPTION_KEY'))

def encrypt_data(data):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    iv = cipher.iv.hex()
    ct = ct_bytes.hex()
    return iv, ct

def decrypt_data(iv, ct):
    iv = bytes.fromhex(iv)
    ct = bytes.fromhex(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')


