#!/usr/bin/env python3
"""
key_loader.py - Runtime key loader for encrypted secrets
"""

import os
import sys
import base64
import hashlib
from pathlib import Path

class KeyLoader:
    """Loads and decrypts encrypted API keys"""

    def __init__(self):
        self.key_file = Path.home() / ".config" / "spiral_codex" / "encryption.key"
        self.salt = b'spiral_codex_2025_salt_v2'

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)

    def load_key(self) -> str:
        """Load encryption key"""
        if self.key_file.exists():
            return self.key_file.read_text().strip()
        else:
            raise FileNotFoundError("Encryption key not found. Run secure_keys.py first.")

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value"""
        if not encrypted_value.startswith("ENCRYPTED:"):
            return encrypted_value

        try:
            key = self.load_key()
            key_bytes = self._derive_key(key)

            # Remove ENCRYPTED: prefix and decode
            encrypted = base64.urlsafe_b64decode(encrypted_value[10:].encode('utf-8'))

            # XOR decryption
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])

            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {e}")

    def load_env_file(self, env_path: str) -> dict:
        """Load and decrypt values from an environment file"""
        env_vars = {}

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('"\'')

                        # Decrypt if needed
                        if value.startswith("ENCRYPTED:"):
                            value = self.decrypt_value(value)

                        env_vars[key] = value

        return env_vars

# Example usage
if __name__ == "__main__":
    loader = KeyLoader()

    # Load OpenRouter config
    env_path = "/home/zebadiee/.npm-global/bin/.env"
    config = loader.load_env_file(env_path)

    if "OPENROUTER_API_KEY" in config:
        print(f"✅ API key loaded successfully: {config['OPENROUTER_API_KEY'][:10]}...")
    else:
        print("❌ OPENROUTER_API_KEY not found")
