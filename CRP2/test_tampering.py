from crypto.kem import MLKEM
from crypto.key_derivation import derive_aes_key
from crypto.encryption import AESGCMEncryption


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Stage 1 - Tampering Attack Test")
print("=" * 60)


# --------------------------------------------------
# STEP 1
# Establish ML-KEM session
# --------------------------------------------------

print("\n[1] Establishing secure session...")

kem = MLKEM("ML-KEM-768")

public_key, secret_key = kem.generate_keypair()

ciphertext, alice_shared_secret = kem.encapsulate(public_key)

bob_shared_secret = kem.decapsulate(
    secret_key,
    ciphertext
)

print("    ✓ ML-KEM session established")


# --------------------------------------------------
# STEP 2
# Derive AES keys
# --------------------------------------------------

print("\n[2] Deriving AES-256 keys...")

alice_aes_key = derive_aes_key(alice_shared_secret)

bob_aes_key = derive_aes_key(bob_shared_secret)

print("    ✓ AES keys derived")


# --------------------------------------------------
# STEP 3
# Alice encrypts a message
# --------------------------------------------------

message = "Transfer 100 units to Bob."

print("\n[3] Alice encrypts message...")

alice_crypto = AESGCMEncryption(alice_aes_key)

nonce, encrypted_message = alice_crypto.encrypt(message)

print("    Original message:")
print(f"    {message}")

print("\n    ✓ Message encrypted")


# --------------------------------------------------
# STEP 4
# Attacker modifies ciphertext
# --------------------------------------------------

print("\n[4] Attacker intercepts the ciphertext...")

tampered_message = bytearray(encrypted_message)

# Change one byte
tampered_message[0] ^= 1

tampered_message = bytes(tampered_message)

print("    ⚠ Ciphertext modified by attacker")


# --------------------------------------------------
# STEP 5
# Bob attempts to decrypt
# --------------------------------------------------

print("\n[5] Bob attempts to decrypt modified message...")

bob_crypto = AESGCMEncryption(bob_aes_key)

try:

    decrypted_message = bob_crypto.decrypt(
        nonce,
        tampered_message
    )

    print("\n    ⚠ WARNING!")
    print("    Tampered message was accepted.")
    print(f"    Message: {decrypted_message}")

except Exception:

    print("\n    ✓ ATTACK DETECTED!")
    print("    ✓ Authentication verification failed.")
    print("    ✓ Modified message was rejected.")


print("\n" + "=" * 60)
print("TAMPERING TEST COMPLETED")
print("=" * 60)
