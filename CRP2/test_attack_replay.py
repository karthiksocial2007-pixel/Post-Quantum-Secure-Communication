from communication.protocol import SecureProtocol


print("=" * 60)
print("STAGE 3 - REPLAY ATTACK")
print("=" * 60)


# --------------------------------------------------
# Step 1: Establish secure communication
# --------------------------------------------------

print("\n[1] Establishing secure communication...")

protocol = SecureProtocol()

protocol.start_session()

print("    ✓ ML-KEM-768 session established")
print("    ✓ AES-256 session key derived")
print("    ✓ ML-DSA-65 signing keys generated")


# --------------------------------------------------
# Step 2: Alice creates message
# --------------------------------------------------

message = "Payment of 100 rupees authorized."

print("\n[2] Alice creates message...")
print(f"    Message: {message}")


secure_message = protocol.create_message(
    sender="Alice",
    receiver="Bob",
    message=message
)

print("    ✓ Message encrypted")
print("    ✓ Message signed")
print(f"    ✓ Message ID: {secure_message.message_id}")


# --------------------------------------------------
# Step 3: Bob receives message first time
# --------------------------------------------------

print("\n[3] Bob receives message for the first time...")

decrypted_message, valid = (
    protocol.verify_message(secure_message)
)

if valid:

    print("    ✓ Message accepted")
    print(f"    ✓ Decrypted message: {decrypted_message}")


# --------------------------------------------------
# Step 4: Attacker replays old message
# --------------------------------------------------

print("\n[4] Attacker replays the same message...")

print(f"    Replayed Message ID: {secure_message.message_id}")


# --------------------------------------------------
# Step 5: Bob receives same message again
# --------------------------------------------------

print("\n[5] Bob receives replayed message...")

try:

    protocol.verify_message(secure_message)

    print("    ✗ REPLAY ATTACK NOT DETECTED")
    print("    ✗ Previously processed message was accepted.")

except ValueError as error:

    print("    ✓ REPLAY ATTACK DETECTED!")
    print(f"    ✓ {error}")
    print("    ✓ Previously processed message was rejected.")


print("\n" + "=" * 60)
print("REPLAY ATTACK TEST COMPLETED")
print("=" * 60)