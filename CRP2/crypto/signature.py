import oqs


class MLDSA:

    def __init__(self, algorithm="ML-DSA-65"):
        self.algorithm = algorithm

    def generate_keypair(self):

        with oqs.Signature(self.algorithm) as signer:

            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()

        return public_key, secret_key

    def sign(self, secret_key, message):

        with oqs.Signature(
            self.algorithm,
            secret_key
        ) as signer:

            signature = signer.sign(message)

        return signature

    def verify(self, public_key, message, signature):

        with oqs.Signature(self.algorithm) as verifier:

            is_valid = verifier.verify(
                message,
                signature,
                public_key
            )

        return is_valid
    