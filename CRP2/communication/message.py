import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class SecureMessage:

    sender: str
    receiver: str
    nonce: bytes
    ciphertext: bytes
    signature: bytes
    timestamp: str
    message_id: str

    def to_dict(self):

        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "nonce": self.nonce.hex(),
            "ciphertext": self.ciphertext.hex(),
            "signature": self.signature.hex(),
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }

    # ------------------------------------------------------------------
    # Header binding
    # ------------------------------------------------------------------
    # The header (sender, receiver, timestamp, message_id) is used as
    # AES-GCM associated data AND is covered by the ML-DSA signature.
    # Without this, an attacker could change message_id and replay a
    # captured packet, because the ID was not authenticated by anything.

    @staticmethod
    def build_aad(sender, receiver, timestamp, message_id):

        header = {
            "v": 1,
            "sender": sender,
            "receiver": receiver,
            "timestamp": timestamp,
            "message_id": message_id
        }

        return json.dumps(
            header,
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")

    def aad(self):

        return SecureMessage.build_aad(
            self.sender,
            self.receiver,
            self.timestamp,
            self.message_id
        )

    @staticmethod
    def signing_payload(aad, plaintext_bytes):

        # length-prefix the header so header/plaintext boundaries are unambiguous
        return len(aad).to_bytes(4, "big") + aad + plaintext_bytes

    @staticmethod
    def create_timestamp():

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def create_message_id():

        return str(uuid.uuid4())
