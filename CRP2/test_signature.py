from crypto.signature import MLDSA


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Stage 1 - ML-DSA Digital Signature Test")
print("=" * 60)


# --------------------------------------------------
# STEP 1
# Generate ML-DSA key pair
# --------------------------------------------------

print("\n[1] Generating ML-DSA-65 key pair...")

dsa = MLDSA("ML-DSA-65")

public_key, secret_key = dsa.generate_keypair()

print("    ✓ Public key generated")
print("    ✓ Secret key generated")


# --------------------------------------------------
# STEP 2
# Create message
# --------------------------------------------------

message = b"Hello Bob! This message is digitally signed."

print("\n[2] Message created...")

print(f"    Message: {message.decode()}")


# --------------------------------------------------
# STEP 3
# Sign message
# --------------------------------------------------

print("\n[3] Alice signs the message...")

signature = dsa.sign(
    secret_key,
    message
)

print("    ✓ Signature generated")

print(f"    Signature size: {len(signature)} bytes")


# --------------------------------------------------
# STEP 4
# Verify signature
# --------------------------------------------------

print("\n[4] Bob verifies the signature...")

valid = dsa.verify(
    public_key,
    message,
    signature
)

if valid:

    print("    ✓ Signature is VALID")

else:

    print("    ✗ Signature is INVALID")


# --------------------------------------------------
# STEP 5
# Modify message
# --------------------------------------------------

print("\n[5] Attacker modifies the message...")

modified_message = b"Hello Bob! This message has been modified."

print(f"    Modified message: {modified_message.decode()}")


# --------------------------------------------------
# STEP 6
# Verify modified message
# --------------------------------------------------

print("\n[6] Bob verifies the modified message...")

modified_valid = dsa.verify(
    public_key,
    modified_message,
    signature
)

if modified_valid:

    print("    ⚠ WARNING!")
    print("    Modified message was accepted.")

else:

    print("    ✓ ATTACK DETECTED!")
    print("    ✓ Signature verification failed.")
    print("    ✓ Modified message rejected.")


# --------------------------------------------------
# Information
# --------------------------------------------------

print("\n[7] Key information")

print(f"    Algorithm: ML-DSA-65")
print(f"    Public key size: {len(public_key)} bytes")
print(f"    Secret key size: {len(secret_key)} bytes")
print(f"    Signature size: {len(signature)} bytes")


print("\n" + "=" * 60)
print("ML-DSA TEST COMPLETED")
print("=" * 60)