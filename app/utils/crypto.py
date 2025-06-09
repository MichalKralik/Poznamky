import base64
import os
# Use only Crypto namespace - pycryptodome uses this namespace by default
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import current_app

class AESCipher:
    def __init__(self, key=None):
        """Initialize cipher with key or use app config key"""
        if key is None:
            key = current_app.config['ENCRYPTION_KEY']
            
        # Ensure key is of correct length for AES-256 (32 bytes)
        self.key = self._derive_key(key)
    
    def _derive_key(self, key_str):
        """Derive a 32-byte key from the provided string"""
        if isinstance(key_str, str):
            key_str = key_str.encode('utf-8')
        return key_str[:32].ljust(32, b'\0')
    
    def encrypt(self, plaintext):
        """Encrypt plaintext using AES-256-CBC"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
            
        # Generate random initialization vector
        iv = os.urandom(16)
        
        # Create cipher and encrypt
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        
        # Return base64 encoded IV and ciphertext
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
        
        return ciphertext_b64, iv_b64
    
    def decrypt(self, ciphertext_b64, iv_b64):
        """Decrypt ciphertext using AES-256-CBC"""
        # Decode base64 encoded IV and ciphertext
        iv = base64.b64decode(iv_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        
        # Create cipher and decrypt
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        return plaintext.decode('utf-8')
