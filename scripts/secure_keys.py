#!/usr/bin/env python3
"""
secure_keys.py - Secure API key management for Spiral Codex
Moves exposed API keys to encrypted storage and fixes configuration files
"""

import os
import sys
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Optional

class SimpleEncryptor:
    """Simple but effective encryption using system key derivation"""

    def __init__(self):
        self.salt = b'spiral_codex_2025_salt_v2'
        self.key_file = Path.home() / ".config" / "spiral_codex" / "encryption.key"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)

    def generate_key(self) -> str:
        """Generate new encryption key"""
        key = secrets.token_urlsafe(32)
        self.key_file.write_text(key)
        self.key_file.chmod(0o600)  # Only owner can read/write
        return key

    def load_key(self) -> str:
        """Load or generate encryption key"""
        if self.key_file.exists():
            return self.key_file.read_text().strip()
        else:
            return self.generate_key()

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using XOR with derived key"""
        if not plaintext:
            return ""

        key = self.load_key()
        key_bytes = self._derive_key(key)

        # Convert to bytes
        data = plaintext.encode('utf-8')

        # XOR encryption
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        # Return base64 encoded
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_b64: str) -> str:
        """Decrypt encrypted base64 string"""
        if not encrypted_b64:
            return ""

        try:
            key = self.load_key()
            key_bytes = self._derive_key(key)

            # Decode from base64
            encrypted = base64.urlsafe_b64decode(encrypted_b64.encode('utf-8'))

            # XOR decryption
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])

            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt: {e}")

class SecurityAuditor:
    """Audits and fixes security issues in the Spiral Codex stack"""

    def __init__(self):
        self.encryptor = SimpleEncryptor()
        self.issues_found = []

    def scan_for_exposed_keys(self) -> Dict[str, list]:
        """Scan for exposed API keys in configuration files"""
        exposed_keys = {}

        # Files to check
        files_to_check = [
            "/home/zebadiee/.npm-global/bin/.env",
            "/home/zebadiee/.env",
            f"{Path.home()}/Documents/spiral_codex_unified/.env",
            f"{Path.home()}/Documents/ai-token-manager/configs/infra/secrets.json"
        ]

        for file_path in files_to_check:
            if os.path.exists(file_path):
                exposed_keys[file_path] = self._check_file_for_keys(file_path)

        return exposed_keys

    def _check_file_for_keys(self, file_path: str) -> list:
        """Check a single file for exposed API keys"""
        exposed = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for OpenRouter API keys
            if 'sk-or-v1-' in content:
                exposed.append({
                    'type': 'OpenRouter API Key',
                    'pattern': 'sk-or-v1-',
                    'severity': 'CRITICAL'
                })

            # Check for other common API key patterns
            api_patterns = [
                ('AI Provider Key', 'sk-'),
                ('Database URL', 'mongodb://'),
                ('Database URL', 'postgresql://'),
                ('Secret Token', 'secret'),
                ('Private Key', 'PRIVATE KEY')
            ]

            for pattern_name, pattern in api_patterns:
                if pattern in content.lower() and 'example' not in content.lower():
                    exposed.append({
                        'type': pattern_name,
                        'pattern': pattern,
                        'severity': 'HIGH' if 'key' in pattern.lower() else 'MEDIUM'
                    })

        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")

        return exposed

    def secure_env_file(self, file_path: str) -> bool:
        """Secure an environment file by encrypting API keys"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        print(f"🔒 Securing {file_path}...")

        try:
            # Read original file
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Process lines
            secured_lines = []
            changes_made = False

            for line in lines:
                stripped = line.strip()
                if '=' in stripped and not stripped.startswith('#'):
                    key, value = stripped.split('=', 1)
                    value = value.strip('"\'')

                    # Check if this looks like an API key
                    if self._is_api_key(value):
                        print(f"  🔐 Encrypting {key}")
                        encrypted_value = self.encryptor.encrypt(value)
                        secured_lines.append(f'{key}="ENCRYPTED:{encrypted_value}"\n')
                        changes_made = True
                    else:
                        secured_lines.append(line)
                else:
                    secured_lines.append(line)

            if changes_made:
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w') as f:
                    f.writelines(lines)
                print(f"  💾 Backup saved to {backup_path}")

                # Write secured file
                with open(file_path, 'w') as f:
                    f.writelines(secured_lines)
                print(f"  ✅ {file_path} secured")
                return True
            else:
                print(f"  ℹ️  No API keys found in {file_path}")
                return False

        except Exception as e:
            print(f"  ❌ Failed to secure {file_path}: {e}")
            return False

    def _is_api_key(self, value: str) -> bool:
        """Check if a value looks like an API key"""
        # Common API key patterns
        api_patterns = [
            'sk-or-v1-',
            'sk-',
            'xoxb-',          # Slack bot
            'xoxp-',          # Slack user
            'ghp_',           # GitHub personal
            'gho_',           # GitHub OAuth
            'ghu_',           # GitHub user
            'ghs_',           # GitHub server
            'ghr_',           # GitHub refresh
            'AIza',           # Google API
            'AKIA',           # AWS
        ]

        # Check length and patterns
        if len(value) < 10:
            return False

        for pattern in api_patterns:
            if value.startswith(pattern):
                return True

        # Check for long hexadecimal strings (common for API keys)
        if len(value) > 20 and all(c in '0123456789abcdefABCDEF' for c in value):
            return True

        return False

    def create_key_loader(self, output_path: str = None) -> str:
        """Create a utility to decrypt keys at runtime"""
        if output_path is None:
            output_path = "/home/zebadiee/Documents/spiral_codex_unified/utils/key_loader.py"

        loader_code = '''#!/usr/bin/env python3
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
'''

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(loader_code)

        os.chmod(output_path, 0o755)
        print(f"🔧 Created key loader: {output_path}")
        return output_path

    def audit(self) -> bool:
        """Run full security audit and fix issues"""
        print("🔍 Running Spiral Codex Security Audit")
        print("=" * 50)

        # Scan for exposed keys
        print("1️⃣  Scanning for exposed API keys...")
        exposed_keys = self.scan_for_exposed_keys()

        total_issues = 0
        for file_path, issues in exposed_keys.items():
            if issues:
                print(f"  🚨 {file_path}:")
                for issue in issues:
                    print(f"    - {issue['type']} ({issue['severity']})")
                    total_issues += 1
                    self.issues_found.append((file_path, issue))

        if total_issues == 0:
            print("  ✅ No exposed API keys found")
            return True

        print(f"\n🚨 Found {total_issues} security issues")

        # Fix exposed keys
        print("\n2️⃣  Securing exposed API keys...")
        fixes_applied = 0

        for file_path in set(file_path for file_path, _ in self.issues_found):
            if self.secure_env_file(file_path):
                fixes_applied += 1

        # Create key loader
        print("\n3️⃣  Creating runtime key loader...")
        self.create_key_loader()

        print(f"\n✅ Security audit completed:")
        print(f"   - Issues found: {total_issues}")
        print(f"   - Files secured: {fixes_applied}")
        print(f"   - Key loader created")

        if total_issues > 0:
            print(f"\n⚠️  IMPORTANT: Update your code to use utils/key_loader.py")
            print(f"   Example:")
            print(f"   ```python")
            print(f"   from utils.key_loader import KeyLoader")
            print(f"   loader = KeyLoader()")
            print(f"   config = loader.load_env_file('/path/to/.env')")
            print(f"   api_key = config['OPENROUTER_API_KEY']")
            print(f"   ```")

        return fixes_applied > 0

def main():
    """Main entry point"""
    auditor = SecurityAuditor()
    success = auditor.audit()

    if success:
        print("\n🎉 Security audit completed successfully!")
        sys.exit(0)
    else:
        print("\nℹ️  No security issues found.")
        sys.exit(0)

if __name__ == "__main__":
    main()