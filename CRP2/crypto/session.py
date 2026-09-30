from crypto.kem import MLKEM
from crypto.key_derivation import derive_aes_key
from crypto.encryption import AESGCMEncryption
from crypto.signature import MLDSA


class SecureSession:

    def __init__(self):

        self.kem = MLKEM("ML-KEM-768")
        self.dsa = MLDSA("ML-DSA-65")

        self.aes = None

        self.session_key = None

        self.kem_ciphertext = None

        self.dsa_public_key = None
        self.dsa_secret_key = None

        self.session_established = False

    def establish_session(self):

        # -----------------------------------------
        # Bob's ML-KEM key pair
        # -----------------------------------------

        kem_public_key, kem_secret_key = (
            self.kem.generate_keypair()
        )

        # -----------------------------------------
        # Alice establishes shared secret
        # -----------------------------------------

        kem_ciphertext, alice_shared_secret = (
            self.kem.encapsulate(kem_public_key)
        )

        # -----------------------------------------
        # Bob recovers shared secret
        # -----------------------------------------

        bob_shared_secret = self.kem.decapsulate(
            kem_secret_key,
            kem_ciphertext
        )

        # -----------------------------------------
        # Verify shared secrets
        # -----------------------------------------

        if alice_shared_secret != bob_shared_secret:

            raise ValueError(
                "ML-KEM shared secrets do not match"
            )

        # -----------------------------------------
        # Derive AES key
        # -----------------------------------------

        self.session_key = derive_aes_key(
            alice_shared_secret
        )

        self.aes = AESGCMEncryption(
            self.session_key
        )

        # Save KEM ciphertext for session information
        self.kem_ciphertext = kem_ciphertext

        self.session_established = True

        return True

    def encrypt_message(self, message):

        if not self.session_established:

            raise ValueError(
                "Secure session has not been established"
            )

        nonce, ciphertext = self.aes.encrypt(
            message
        )

        return nonce, ciphertext

    def decrypt_message(self, nonce, ciphertext):

        if not self.session_established:

            raise ValueError(
                "Secure session has not been established"
            )

        return self.aes.decrypt(
            nonce,
            ciphertext
        )

    def generate_signature_keys(self):

        public_key, secret_key = (
            self.dsa.generate_keypair()
        )

        self.dsa_public_key = public_key
        self.dsa_secret_key = secret_key

        return public_key, secret_key

    def sign_message(self, message):

        if self.dsa_secret_key is None:

            raise ValueError(
                "ML-DSA keys have not been generated"
            )

        return self.dsa.sign(
            self.dsa_secret_key,
            message
        )

    def verify_signature(
        self,
        message,
        signature
    ):

        if self.dsa_public_key is None:

            raise ValueError(
                "ML-DSA public key is not available"
            )

        return self.dsa.verify(
            self.dsa_public_key,
            message,
            signature
        )
    