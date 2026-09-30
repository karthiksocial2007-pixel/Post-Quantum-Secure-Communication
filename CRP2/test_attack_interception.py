from communication.protocol import SecureProtocol


print("=" * 60)
print("STAGE 3 - INTERCEPTION / EAVESDROPPING ATTACK")
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
# Step 2: Alice creates secure message
# --------------------------------------------------

message = "This is a confidential post-quantum message."

print("\n[2] Alice creates message...")
print(f"    Original plaintext: {message}")


secure_message = protocol.create_message(
    sender="Alice",
    receiver="Bob",
    message=message
)

print("    ✓ Message encrypted")
print("    ✓ Message digitally signed")


# --------------------------------------------------
# Step 3: Attacker intercepts packet
# --------------------------------------------------

print("\n[3] Attacker intercepts the communication packet...")

packet = secure_message.to_dict()

print("    ✓ Packet captured")


# --------------------------------------------------
# Step 4: Show what attacker can see
# --------------------------------------------------

print("\n[4] Information visible to attacker:")

print(f"    Sender: {packet['sender']}")
print(f"    Receiver: {packet['receiver']}")
print(f"    Timestamp: {packet['timestamp']}")
print(f"    Message ID: {packet['message_id']}")

print(f"    Nonce: {packet['nonce'][:32]}...")
print(f"    Ciphertext: {packet['ciphertext'][:32]}...")
print(f"    Signature: {packet['signature'][:32]}...")


# --------------------------------------------------
# Step 5: Check whether plaintext is exposed
# --------------------------------------------------

print("\n[5] Checking intercepted packet for plaintext...")

if message in str(packet):

    print("    ✗ PLAINTEXT EXPOSED")
    print("    ✗ Interception compromised confidentiality.")

else:

    print("    ✓ Plaintext is NOT present in intercepted packet")
    print("    ✓ Attacker only sees encrypted ciphertext")


# --------------------------------------------------
# Step 6: Attacker attempts to read ciphertext
# --------------------------------------------------

print("\n[6] Attacker attempts to interpret ciphertext...")

try:

    ciphertext_text = bytes.fromhex(
        packet["ciphertext"]
    ).decode("utf-8")

    print("    ✗ Ciphertext was readable as plaintext")
    print(f"    Data: {ciphertext_text}")

except UnicodeDecodeError:

    print("    ✓ Ciphertext cannot be interpreted as normal text")
    print("    ✓ Encrypted data does not reveal the plaintext")


print("\n" + "=" * 60)
print("INTERCEPTION ATTACK TEST COMPLETED")
print("=" * 60)