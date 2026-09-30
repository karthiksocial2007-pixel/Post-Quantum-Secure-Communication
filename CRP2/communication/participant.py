from crypto.kem import MLKEM
from crypto.key_derivation import derive_aes_key
from crypto.encryption import AESGCMEncryption
from crypto.signature import MLDSA
from datetime import datetime, timezone

from cryptography.exceptions import InvalidTag

from communication.message import SecureMessage


class PacketRejected(ValueError):
    """Raised when a received packet fails any security check."""


# Packets older than this (or too far in the future) are rejected.
MAX_MESSAGE_AGE_SECONDS = 600
MAX_CLOCK_SKEW_SECONDS = 60


class Participant:

    def __init__(self, name):

        self.name = name

        # Cryptographic components
        self.kem = MLKEM("ML-KEM-768")
        self.dsa = MLDSA("ML-DSA-65")

        # KEM keys
        self.kem_public_key = None
        self.kem_secret_key = None

        # ML-DSA keys
        self.signature_public_key = None
        self.signature_secret_key = None

        # AES session
        self.session_key = None
        self.aes = None

        # Public signature key of the other participant
        self.peer_signature_public_key = None

        # Replay protection
        self.received_message_ids = set()

    # --------------------------------------------------
    # Generate keys
    # --------------------------------------------------

    def generate_keys(self):

        (
            self.kem_public_key,
            self.kem_secret_key
        ) = self.kem.generate_keypair()

        (
            self.signature_public_key,
            self.signature_secret_key
        ) = self.dsa.generate_keypair()

    # --------------------------------------------------
    # Create secure session with another participant
    # --------------------------------------------------

    def create_session_with(self, peer):

        ciphertext, shared_secret = (
            self.kem.encapsulate(
                peer.kem_public_key
            )
        )

        self.session_key = derive_aes_key(
            shared_secret
        )

        self.aes = AESGCMEncryption(
            self.session_key
        )

        return ciphertext

    # --------------------------------------------------
    # Accept session
    # --------------------------------------------------

    def accept_session(self, ciphertext):

        shared_secret = self.kem.decapsulate(
            self.kem_secret_key,
            ciphertext
        )

        self.session_key = derive_aes_key(
            shared_secret
        )

        self.aes = AESGCMEncryption(
            self.session_key
        )

    # --------------------------------------------------
    # Send secure message
    # --------------------------------------------------

    def send_message(self, receiver, message):

        if self.aes is None:
            raise ValueError("Secure session has not been established")

        timestamp = SecureMessage.create_timestamp()
        message_id = SecureMessage.create_message_id()

        aad = SecureMessage.build_aad(
            self.name,
            receiver.name,
            timestamp,
            message_id
        )

        # AES-GCM authenticates the header as associated data
        nonce, ciphertext = self.aes.encrypt(message, aad)

        # ML-DSA signs header + plaintext
        signature = self.dsa.sign(
            self.signature_secret_key,
            SecureMessage.signing_payload(aad, message.encode("utf-8"))
        )

        return SecureMessage(
            sender=self.name,
            receiver=receiver.name,
            nonce=nonce,
            ciphertext=ciphertext,
            signature=signature,
            timestamp=timestamp,
            message_id=message_id
        )

    # --------------------------------------------------
    # Stateless check: decrypt + verify (no replay bookkeeping)
    # --------------------------------------------------

    def decrypt_and_verify(self, secure_message):

        if self.aes is None:
            raise ValueError("Secure session has not been established")

        if self.peer_signature_public_key is None:
            raise ValueError("Peer ML-DSA public key is not available")

        aad = secure_message.aad()

        try:
            plaintext = self.aes.decrypt(
                secure_message.nonce,
                secure_message.ciphertext,
                aad
            )
        except InvalidTag:
            raise PacketRejected(
                "AES-256-GCM authentication failed "
                "(ciphertext, nonce or header was modified)"
            )

        try:
            signature_valid = self.dsa.verify(
                self.peer_signature_public_key,
                SecureMessage.signing_payload(
                    aad,
                    plaintext.encode("utf-8")
                ),
                secure_message.signature
            )
        except Exception:
            signature_valid = False

        if not signature_valid:
            raise PacketRejected("Invalid ML-DSA signature")

        return plaintext

    # --------------------------------------------------
    # Receive secure message (full checks + replay tracking)
    # --------------------------------------------------

    def receive_message(self, secure_message):

        if self.aes is None:
            raise ValueError("Secure session has not been established")

        # 1. Receiver check
        if secure_message.receiver != self.name:
            raise PacketRejected(
                "Message receiver does not match participant"
            )

        # 2. Freshness check
        self._check_fresh(secure_message.timestamp)

        # 3. Replay check
        if secure_message.message_id in self.received_message_ids:
            raise PacketRejected(
                "Replay attack detected: "
                "message has already been received"
            )

        # 4. Decrypt (header authenticated) + verify ML-DSA signature
        plaintext = self.decrypt_and_verify(secure_message)

        # 5. Only remember the ID after everything succeeded
        self.received_message_ids.add(secure_message.message_id)

        return plaintext

    @staticmethod
    def _check_fresh(timestamp):

        try:
            sent_at = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError):
            raise PacketRejected("Invalid timestamp")

        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)

        age = (datetime.now(timezone.utc) - sent_at).total_seconds()

        if age > MAX_MESSAGE_AGE_SECONDS:
            raise PacketRejected("Message is too old (stale timestamp)")

        if age < -MAX_CLOCK_SKEW_SECONDS:
            raise PacketRejected("Message timestamp is in the future")
