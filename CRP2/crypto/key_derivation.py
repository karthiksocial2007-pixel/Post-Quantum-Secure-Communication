from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_aes_key(shared_secret):

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"PostQuantumSecureCommunication"
    )

    aes_key = hkdf.derive(shared_secret)

    return aes_key