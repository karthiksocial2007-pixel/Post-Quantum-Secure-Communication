import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESGCMEncryption:
    """AES-256-GCM authenticated encryption.

    `aad` (associated data) is authenticated but not encrypted. The secure
    protocol passes the packet header (sender, receiver, timestamp, message ID)
    here, so tampering with the header makes decryption fail.
    """

    def __init__(self, key):

        if len(key) != 32:
            raise ValueError("AES-256 key must be exactly 32 bytes")

        self.key = key
        self.aes = AESGCM(key)

    def encrypt(self, message, aad=None):

        nonce = os.urandom(12)

        plaintext = message.encode("utf-8")

        ciphertext = self.aes.encrypt(nonce, plaintext, aad)

        return nonce, ciphertext

    def decrypt(self, nonce, ciphertext, aad=None):

        plaintext = self.aes.decrypt(nonce, ciphertext, aad)

        return plaintext.decode("utf-8")
