import oqs


class MLKEM:

    def __init__(self, algorithm="ML-KEM-768"):
        self.algorithm = algorithm

    def generate_keypair(self):
        with oqs.KeyEncapsulation(self.algorithm) as kem:
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()

        return public_key, secret_key

    def encapsulate(self, public_key):
        with oqs.KeyEncapsulation(self.algorithm) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)

        return ciphertext, shared_secret

    def decapsulate(self, secret_key, ciphertext):
        with oqs.KeyEncapsulation(
            self.algorithm,
            secret_key
        ) as kem:

            shared_secret = kem.decap_secret(ciphertext)

        return shared_secret