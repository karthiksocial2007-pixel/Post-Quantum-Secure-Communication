class TamperingAttack:

    @staticmethod
    def modify_ciphertext(ciphertext):

        # Convert ciphertext into a mutable byte array
        modified = bytearray(ciphertext)

        # Flip one bit of the first byte
        modified[0] ^= 1

        return bytes(modified)
