from crypto.session import SecureSession
from attacks.tampering import TamperingAttack


print("=" * 60)
print("STAGE 3 - CIPHERTEXT TAMPERING ATTACK")
print("=" * 60)


# --------------------------------------------------
# Step 1: Establish secure session
# --------------------------------------------------

print("\n[1] Establishing secure session...")

session = SecureSession()

session.establish_session()

print("    ✓ ML-KEM-768 session established")
print("    ✓ AES-256 session key derived")


# --------------------------------------------------
# Step 2: Encrypt original message
# --------------------------------------------------

message = "This message must remain secure."

print("\n[2] Original message:")
print(f"    {message}")


nonce, ciphertext = session.encrypt_message(message)

print("\n[3] Message encrypted")
print(f"    Ciphertext size: {len(ciphertext)} bytes")


# --------------------------------------------------
# Step 3: Attacker modifies ciphertext
# --------------------------------------------------

print("\n[4] Attacker modifies ciphertext...")

tampered_ciphertext = (
    TamperingAttack.modify_ciphertext(ciphertext)
)

print("    ✓ Ciphertext modified")


# --------------------------------------------------
# Step 4: Bob attempts decryption
# --------------------------------------------------

print("\n[5] Bob attempts to decrypt modified message...")

try:

    decrypted_message = session.decrypt_message(
        nonce,
        tampered_ciphertext
    )

    print("    ✗ ATTACK NOT DETECTED")
    print(f"    Decrypted message: {decrypted_message}")

except Exception:

    print("    ✓ ATTACK DETECTED!")
    print("    ✓ AES-GCM authentication failed.")
    print("    ✓ Modified ciphertext was rejected.")


print("\n" + "=" * 60)
print("CIPHERTEXT TAMPERING TEST COMPLETED")
print("=" * 60)