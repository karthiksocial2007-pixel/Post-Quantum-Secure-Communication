from crypto.kem import MLKEM


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Stage 1 - ML-KEM Test")
print("=" * 60)


# Create ML-KEM object
kem = MLKEM("ML-KEM-768")


# --------------------------------------------------
# Step 1: Generate Bob's key pair
# --------------------------------------------------

print("\n[1] Generating Bob's ML-KEM key pair...")

public_key, secret_key = kem.generate_keypair()

print("    Public key generated")
print("    Secret key generated")


# --------------------------------------------------
# Step 2: Alice encapsulates a shared secret
# --------------------------------------------------

print("\n[2] Alice performs encapsulation...")

ciphertext, alice_shared_secret = kem.encapsulate(public_key)

print("    Ciphertext generated")
print("    Alice's shared secret generated")


# --------------------------------------------------
# Step 3: Bob decapsulates
# --------------------------------------------------

print("\n[3] Bob performs decapsulation...")

bob_shared_secret = kem.decapsulate(
    secret_key,
    ciphertext
)

print("    Bob's shared secret generated")


# --------------------------------------------------
# Step 4: Compare the secrets
# --------------------------------------------------

print("\n[4] Comparing shared secrets...")

if alice_shared_secret == bob_shared_secret:

    print("    SUCCESS!")
    print("    Alice and Bob have the same shared secret.")

else:

    print("    FAILED!")
    print("    Shared secrets do not match.")


# --------------------------------------------------
# Information
# --------------------------------------------------

print("\n[5] Key information")

print(f"    Algorithm: ML-KEM-768")
print(f"    Public key size: {len(public_key)} bytes")
print(f"    Secret key size: {len(secret_key)} bytes")
print(f"    Ciphertext size: {len(ciphertext)} bytes")
print(f"    Shared secret size: {len(alice_shared_secret)} bytes")

print("\n" + "=" * 60)
print("ML-KEM TEST COMPLETED")
print("=" * 60)