#!/usr/bin/env python3
"""
secure_secrets.py - Real encryption for API keys and secrets
Uses cryptography.fernet for actual encryption with proper key management
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureSecretManager:
    """Secure secret management with proper encryption"""

    def __init__(self, master_password: str = None, key_file: str = None):
        self.key_file = key_file or Path.home() / ".config" / "spiral_codex" / "secret_key.key"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        if master_password:
            # Derive key from password
            self.fernet = self._get_fernet_from_password(master_password)
        else:
            # Load or generate key file
            self.fernet = self._load_or_generate_key()

    def _get_fernet_from_password(self, password: str) -> Fernet:
        """Derive encryption key from password"""
        salt = b'spiral_codex_salt'  # In production, use random salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _load_or_generate_key(self) -> Fernet:
        """Load existing key or generate new one"""
        if self.key_file.exists():
            key = self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            # Set restrictive permissions
            self.key_file.chmod(0o600)
        return Fernet(key)

    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not plaintext:
            return ""
        encrypted_data = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_string(self, encrypted_b64: str) -> str:
        """Decrypt base64 encoded encrypted string"""
        if not encrypted_b64:
            return ""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_b64.encode())
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt: {e}")

    def encrypt_secrets_dict(self, secrets_dict: dict) -> dict:
        """Encrypt all values in a secrets dictionary"""
        encrypted = {}
        for key, value in secrets_dict.items():
            if isinstance(value, str):
                encrypted[key] = self.encrypt_string(value)
            else:
                encrypted[key] = value  # Keep non-strings as-is
        return encrypted

    def decrypt_secrets_dict(self, encrypted_dict: dict) -> dict:
        """Decrypt all values in an encrypted secrets dictionary"""
        decrypted = {}
        for key, value in encrypted_dict.items():
            if isinstance(value, str) and not key.endswith('_path'):  # Don't decrypt file paths
                try:
                    decrypted[key] = self.decrypt_string(value)
                except:
                    decrypted[key] = value  # Keep as-is if decryption fails
            else:
                decrypted[key] = value
        return decrypted

def main():
    """Test the secure secret manager"""
    import getpass

    print("🔐 Secure Secret Manager Test")

    # Test with system key file
    manager = SecureSecretManager()

    # Test encryption/decryption
    test_secret = "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"
    print(f"Original: {test_secret}")

    encrypted = manager.encrypt_string(test_secret)
    print(f"Encrypted: {encrypted}")

    decrypted = manager.decrypt_string(encrypted)
    print(f"Decrypted: {decrypted}")

    print(f"✅ Encryption working: {test_secret == decrypted}")

    # Test with secrets dict
    test_secrets = {
        "OPENROUTER_API_KEY": test_secret,
        "DB_PASSWORD": "my_database_password",
        "JWT_SECRET": "jwt_signing_secret"
    }

    encrypted_secrets = manager.encrypt_secrets_dict(test_secrets)
    print(f"\n📋 Encrypted secrets dict: {json.dumps(encrypted_secrets, indent=2)}")

    decrypted_secrets = manager.decrypt_secrets_dict(encrypted_secrets)
    print(f"\n📋 Decrypted secrets dict: {json.dumps(decrypted_secrets, indent=2)}")

if __name__ == "__main__":
    main()