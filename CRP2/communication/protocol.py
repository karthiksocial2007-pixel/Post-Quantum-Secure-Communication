from crypto.session import SecureSession
from communication.message import SecureMessage


class SecureProtocol:

    def __init__(self):

        self.session = SecureSession()

        self.signature_public_key = None
        self.signature_secret_key = None

        # Stores message IDs that have already been received
        self.received_message_ids = set()

    def start_session(self):

        self.session.establish_session()

        (
            self.signature_public_key,
            self.signature_secret_key
        ) = self.session.generate_signature_keys()

        return True

    def create_message(
        self,
        sender,
        receiver,
        message
    ):

        if not self.session.session_established:
            raise ValueError(
                "Secure session has not been established"
            )

        nonce, ciphertext = (
            self.session.encrypt_message(message)
        )

        signature = self.session.sign_message(
            message.encode("utf-8")
        )

        secure_message = SecureMessage(
            sender=sender,
            receiver=receiver,
            nonce=nonce,
            ciphertext=ciphertext,
            signature=signature,
            timestamp=SecureMessage.create_timestamp(),
            message_id=SecureMessage.create_message_id()
        )

        return secure_message

    def verify_message(
        self,
        secure_message
    ):

        # Check for replay attack BEFORE processing
        if secure_message.message_id in self.received_message_ids:

            raise ValueError(
                "Replay attack detected: message has already been received"
            )

        decrypted_message = (
            self.session.decrypt_message(
                secure_message.nonce,
                secure_message.ciphertext
            )
        )

        signature_valid = (
            self.session.verify_signature(
                decrypted_message.encode("utf-8"),
                secure_message.signature
            )
        )

        if not signature_valid:

            raise ValueError(
                "Invalid ML-DSA signature"
            )

        # Mark message as received
        self.received_message_ids.add(
            secure_message.message_id
        )

        return decrypted_message, signature_valid