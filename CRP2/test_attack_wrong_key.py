from crypto.session import SecureSession
from crypto.key_derivation import derive_aes_key
from crypto.encryption import AESGCMEncryption


print("=" * 60)
print("STAGE 3 - WRONG SESSION KEY ATTACK")
print("=" * 60)


# --------------------------------------------------
# Step 1: Alice establishes a secure session
# --------------------------------------------------

print("\n[1] Alice establishes secure session...")

alice_session = SecureSession()

alice_session.establish_session()

print("    ✓ Alice's ML-KEM-768 session established")
print("    ✓ Alice's AES-256 session key created")


# --------------------------------------------------
# Step 2: Alice encrypts a message
# --------------------------------------------------

message = "This information is confidential."

print("\n[2] Alice encrypts message...")
print(f"    Plaintext: {message}")


nonce, ciphertext = alice_session.encrypt_message(message)

print("    ✓ Message encrypted")
print(f"    Ciphertext size: {len(ciphertext)} bytes")


# --------------------------------------------------
# Step 3: Attacker creates a different session
# --------------------------------------------------

print("\n[3] Attacker creates a different session...")

attacker_session = SecureSession()

attacker_session.establish_session()

print("    ✓ Attacker has a different ML-KEM-768 session")
print("    ✓ Attacker has a different AES-256 session key")


# --------------------------------------------------
# Step 4: Attacker tries to decrypt Alice's message
# --------------------------------------------------

print("\n[4] Attacker attempts decryption using wrong key...")

try:

    attacker_session.decrypt_message(
        nonce,
        ciphertext
    )

    print("    ✗ ATTACK NOT DETECTED")
    print("    ✗ Attacker decrypted the message.")

except Exception:

    print("    ✓ ATTACK DETECTED!")
    print("    ✓ Decryption failed with the wrong session key.")
    print("    ✓ Confidential message remained protected.")


print("\n" + "=" * 60)
print("WRONG SESSION KEY ATTACK TEST COMPLETED")
print("=" * 60)