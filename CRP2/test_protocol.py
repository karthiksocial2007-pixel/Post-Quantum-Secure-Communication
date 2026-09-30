from communication.protocol import SecureProtocol


print("=" * 60)
print("POST-QUANTUM SECURE COMMUNICATION")
print("Stage 2 - Alice to Bob Protocol")
print("=" * 60)


# --------------------------------------------------
# STEP 1
# Start secure communication
# --------------------------------------------------

print("\n[1] Starting secure communication...")

protocol = SecureProtocol()

protocol.start_session()

print("    ✓ ML-KEM-768 session established")
print("    ✓ AES-256 session key derived")
print("    ✓ ML-DSA-65 signing keys generated")


# --------------------------------------------------
# STEP 2
# Alice creates message
# --------------------------------------------------

message = "Hello Bob! This is a secure post-quantum message."

print("\n[2] Alice creates message...")

print(f"    Plaintext: {message}")


# --------------------------------------------------
# STEP 3
# Create secure message packet
# --------------------------------------------------

print("\n[3] Alice encrypts and signs message...")

secure_message = protocol.create_message(
    sender="Alice",
    receiver="Bob",
    message=message
)

print("    ✓ Message encrypted")
print("    ✓ Message digitally signed")
print("    ✓ Secure message packet created")


# --------------------------------------------------
# STEP 4
# Display packet information
# --------------------------------------------------

print("\n[4] Secure message packet")

packet = secure_message.to_dict()

print(f"    Sender: {packet['sender']}")
print(f"    Receiver: {packet['receiver']}")
print(f"    Nonce: {packet['nonce'][:24]}...")
print(f"    Ciphertext: {packet['ciphertext'][:24]}...")
print(f"    Signature: {packet['signature'][:24]}...")
print(f"    Timestamp: {packet['timestamp']}")


# --------------------------------------------------
# STEP 5
# Bob receives message
# --------------------------------------------------

print("\n[5] Bob receives secure message...")


decrypted_message, signature_valid = (
    protocol.verify_message(secure_message)
)


# --------------------------------------------------
# STEP 6
# Display result
# --------------------------------------------------

print("\n[6] Bob processes message...")

print(f"    Decrypted message: {decrypted_message}")

if signature_valid:

    print("    ✓ ML-DSA signature VALID")

else:

    print("    ✗ ML-DSA signature INVALID")


# --------------------------------------------------
# STEP 7
# Final verification
# --------------------------------------------------

print("\n[7] Final verification...")

if (
    decrypted_message == message
    and signature_valid
):

    print("    ✓ SECURE COMMUNICATION SUCCESSFUL")

else:

    print("    ✗ SECURE COMMUNICATION FAILED")


print("\n" + "=" * 60)
print("STAGE 2 PROTOCOL TEST COMPLETED")
print("=" * 60)