class InterceptionAttack:

    # A substring search for very short text is meaningless: a 1-byte
    # message appears by pure chance inside a 3309-byte ML-DSA signature.
    # From 8 bytes upwards a chance match is practically impossible.
    MIN_SEARCH_LENGTH = 8

    TAG_LENGTH = 16  # AES-GCM authentication tag

    @staticmethod
    def plaintext_exposed(packet, plaintext):
        """True if an eavesdropper can read the message from the packet."""

        needle = plaintext.encode("utf-8")

        body = packet.ciphertext[:-InterceptionAttack.TAG_LENGTH]

        # Broken encryption: the ciphertext body IS the plaintext
        # (raw bytes or hex text)
        if body == needle or body.hex().encode("ascii") == needle:
            return True

        if len(needle) < InterceptionAttack.MIN_SEARCH_LENGTH:
            return False

        fields = [
            packet.ciphertext,
            packet.ciphertext.hex().encode("ascii"),
            packet.nonce,
            packet.nonce.hex().encode("ascii"),
            packet.signature,
            packet.signature.hex().encode("ascii"),
            packet.aad()
        ]

        return any(needle in field for field in fields)
