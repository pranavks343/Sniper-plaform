from __future__ import annotations

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken


class EncryptionError(RuntimeError):
    pass


class DataEncryptor:
    def __init__(self, raw_key: str) -> None:
        key_material = (raw_key or '').strip()
        if not key_material:
            raise EncryptionError('DATA_ENCRYPTION_KEY is required for encrypting broker credentials')
        self._fernet = Fernet(self._normalize_key(key_material))

    def encrypt_json(self, payload: dict) -> str:
        plaintext = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
        return self._fernet.encrypt(plaintext).decode('utf-8')

    def decrypt_json(self, token: str) -> dict:
        try:
            decrypted = self._fernet.decrypt(token.encode('utf-8'))
        except InvalidToken as exc:
            raise EncryptionError('Encrypted payload could not be decrypted with current DATA_ENCRYPTION_KEY') from exc
        return json.loads(decrypted.decode('utf-8'))

    @staticmethod
    def _normalize_key(raw_key: str) -> bytes:
        # Accept either a Fernet key or any passphrase; passphrases are deterministically derived.
        maybe_bytes = raw_key.encode('utf-8')
        try:
            decoded = base64.urlsafe_b64decode(maybe_bytes + b'=' * (-len(maybe_bytes) % 4))
            if len(decoded) == 32:
                return maybe_bytes
        except Exception:
            pass
        return base64.urlsafe_b64encode(hashlib.sha256(maybe_bytes).digest())
