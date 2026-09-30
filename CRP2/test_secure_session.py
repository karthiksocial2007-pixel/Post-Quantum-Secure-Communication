from crypto.session import SecureSession


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Complete SecureSession Test")
print("=" * 60)


# --------------------------------------------------
# STEP 1
# Create session
# --------------------------------------------------

print("\n[1] Creating secure session...")

session = SecureSession()

print("    ✓ SecureSession created")


# --------------------------------------------------
# STEP 2
# Establish ML-KEM session
# --------------------------------------------------

print("\n[2] Establishing ML-KEM session...")

session.establish_session()

print("    ✓ ML-KEM session established")
print("    ✓ Shared secret established")
print("    ✓ AES-256 session key derived")


# --------------------------------------------------
# STEP 3
# Encrypt message
# --------------------------------------------------

message = "Hello Bob! This is our post-quantum secure message."

print("\n[3] Encrypting message...")

nonce, ciphertext = session.encrypt_message(
    message
)

print("    ✓ Message encrypted")
print(f"    Ciphertext size: {len(ciphertext)} bytes")


# --------------------------------------------------
# STEP 4
# Decrypt message
# --------------------------------------------------

print("\n[4] Decrypting message...")

decrypted = session.decrypt_message(
    nonce,
    ciphertext
)

print("    ✓ Message decrypted")
print(f"    Decrypted: {decrypted}")


# --------------------------------------------------
# STEP 5
# Verify encryption
# --------------------------------------------------

print("\n[5] Checking message...")

if message == decrypted:

    print("    ✓ Original and decrypted messages match")

else:

    print("    ✗ Message mismatch")


# --------------------------------------------------
# STEP 6
# ML-DSA keys
# --------------------------------------------------

print("\n[6] Generating ML-DSA keys...")

session.generate_signature_keys()

print("    ✓ ML-DSA-65 keys generated")


# --------------------------------------------------
# STEP 7
# Sign message
# --------------------------------------------------

print("\n[7] Signing message...")

signature = session.sign_message(
    message.encode("utf-8")
)

print("    ✓ Message signed")


# --------------------------------------------------
# STEP 8
# Verify signature
# --------------------------------------------------

print("\n[8] Verifying signature...")

valid = session.verify_signature(
    message.encode("utf-8"),
    signature
)

if valid:

    print("    ✓ Signature VALID")

else:

    print("    ✗ Signature INVALID")


# --------------------------------------------------
# FINAL
# --------------------------------------------------

print("\n" + "=" * 60)
print("COMPLETE SECURE SESSION TEST FINISHED")
print("=" * 60)