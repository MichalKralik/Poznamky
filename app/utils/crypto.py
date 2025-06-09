import base64
import os
# Use only Crypto namespace - pycryptodome uses this namespace by default
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import current_app

class AESCipher:
    """Třída pro šifrování a dešifrování poznámek pomocí AES-256"""
    
    def __init__(self, key=None):
        """Inicializace šifrovacího klíče - buď z parametru nebo z konfigurace aplikace"""
        if key is None:
            key = current_app.config['ENCRYPTION_KEY']
            
        # Odvození 32-bytového klíče (AES-256 vyžaduje klíč o délce 32 bytů)
        self.key = self._derive_key(key)
    
    def _derive_key(self, key_str):
        """Odvození klíče správné délky z poskytnutého řetězce"""
        if isinstance(key_str, str):
            key_str = key_str.encode('utf-8')
        return key_str[:32].ljust(32, b'\0')  # Zajištění délky 32 bytů
    
    def encrypt(self, plaintext):
        """Zašifruje text pomocí AES-256-CBC"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
            
        # Generování náhodného inicializačního vektoru (IV)
        iv = os.urandom(16)  # AES vyžaduje 16-bytový IV
        
        # Vytvoření šifry a zašifrování dat
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        
        # Vrácení zašifrovaného textu a IV v base64 kódování
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
        
        return ciphertext_b64, iv_b64
    
    def decrypt(self, ciphertext_b64, iv_b64):
        """Dešifruje zašifrovaný text pomocí AES-256-CBC"""
        # Dekódování base64 kódovaného IV a šifrovaného textu
        iv = base64.b64decode(iv_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        
        # Vytvoření šifry a dešifrování dat
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return plaintext.decode('utf-8')
