from crypto.session import SecureSession


print("=" * 60)
print("STAGE 3 - DIGITAL SIGNATURE ATTACK")
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
# Step 2: Generate ML-DSA keys
# --------------------------------------------------

print("\n[2] Generating ML-DSA-65 keys...")

session.generate_signature_keys()

print("    ✓ ML-DSA-65 signing keys generated")


# --------------------------------------------------
# Step 3: Create and sign original message
# --------------------------------------------------

original_message = "Transfer 100 rupees to Bob."

print("\n[3] Original message:")
print(f"    {original_message}")


signature = session.sign_message(
    original_message.encode("utf-8")
)

print("\n[4] Message digitally signed")
print(f"    Signature size: {len(signature)} bytes")


# --------------------------------------------------
# Step 4: Verify original message
# --------------------------------------------------

print("\n[5] Verifying original message...")

original_valid = session.verify_signature(
    original_message.encode("utf-8"),
    signature
)

if original_valid:
    print("    ✓ Original signature is VALID")
else:
    print("    ✗ Original signature is INVALID")


# --------------------------------------------------
# Step 5: Attacker modifies message
# --------------------------------------------------

modified_message = "Transfer 900 rupees to Bob."

print("\n[6] Attacker modifies the message...")

print(f"    Original: {original_message}")
print(f"    Modified: {modified_message}")


# --------------------------------------------------
# Step 6: Verify modified message with old signature
# --------------------------------------------------

print("\n[7] Bob verifies modified message...")

modified_valid = session.verify_signature(
    modified_message.encode("utf-8"),
    signature
)

if modified_valid:

    print("    ✗ ATTACK NOT DETECTED")
    print("    ✗ Modified message was accepted.")

else:

    print("    ✓ ATTACK DETECTED!")
    print("    ✓ ML-DSA signature verification failed.")
    print("    ✓ Modified message was rejected.")


print("\n" + "=" * 60)
print("DIGITAL SIGNATURE ATTACK TEST COMPLETED")
print("=" * 60)