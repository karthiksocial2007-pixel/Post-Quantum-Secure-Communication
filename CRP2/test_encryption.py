from crypto.kem import MLKEM
from crypto.key_derivation import derive_aes_key
from crypto.encryption import AESGCMEncryption


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Stage 1 - ML-KEM + HKDF + AES-256-GCM")
print("=" * 60)


# --------------------------------------------------
# STEP 1
# Bob generates ML-KEM keys
# --------------------------------------------------

print("\n[1] Bob generates ML-KEM key pair...")

kem = MLKEM("ML-KEM-768")

public_key, secret_key = kem.generate_keypair()

print("    ✓ Key pair generated")


# --------------------------------------------------
# STEP 2
# Alice establishes shared secret
# --------------------------------------------------

print("\n[2] Alice performs ML-KEM encapsulation...")

ciphertext, alice_shared_secret = kem.encapsulate(public_key)

print("    ✓ Shared secret generated")


# --------------------------------------------------
# STEP 3
# Bob recovers shared secret
# --------------------------------------------------

print("\n[3] Bob performs ML-KEM decapsulation...")

bob_shared_secret = kem.decapsulate(
    secret_key,
    ciphertext
)

print("    ✓ Shared secret recovered")


# --------------------------------------------------
# STEP 4
# Verify shared secrets
# --------------------------------------------------

print("\n[4] Verifying shared secrets...")

if alice_shared_secret != bob_shared_secret:

    print("    ✗ Shared secrets do not match")

    raise SystemExit

print("    ✓ Shared secrets match")


# --------------------------------------------------
# STEP 5
# Derive AES key using HKDF
# --------------------------------------------------

print("\n[5] Deriving AES-256 key using HKDF...")

alice_aes_key = derive_aes_key(alice_shared_secret)
bob_aes_key = derive_aes_key(bob_shared_secret)

print("    ✓ AES key derived")

if alice_aes_key != bob_aes_key:

    print("    ✗ AES keys do not match")

    raise SystemExit

print("    ✓ Alice and Bob have the same AES key")


# --------------------------------------------------
# STEP 6
# Alice encrypts message
# --------------------------------------------------

message = "Hello Bob! This message is protected by post-quantum cryptography."

print("\n[6] Alice encrypts message...")

alice_crypto = AESGCMEncryption(alice_aes_key)

nonce, encrypted_message = alice_crypto.encrypt(message)

print("    ✓ Message encrypted")

print(f"    Plaintext: {message}")
print(f"    Ciphertext size: {len(encrypted_message)} bytes")
print(f"    Nonce size: {len(nonce)} bytes")


# --------------------------------------------------
# STEP 7
# Bob decrypts message
# --------------------------------------------------

print("\n[7] Bob decrypts message...")

bob_crypto = AESGCMEncryption(bob_aes_key)

decrypted_message = bob_crypto.decrypt(
    nonce,
    encrypted_message
)

print("    ✓ Message decrypted")

print(f"    Decrypted message: {decrypted_message}")


# --------------------------------------------------
# STEP 8
# Final verification
# --------------------------------------------------

print("\n[8] Final verification...")

if message == decrypted_message:

    print("    ✓ SUCCESS!")
    print("    Original and decrypted messages match.")

else:

    print("    ✗ FAILED!")
    print("    Messages do not match.")


print("\n" + "=" * 60)
print("STAGE 1 ENCRYPTION TEST COMPLETED")
print("=" * 60)