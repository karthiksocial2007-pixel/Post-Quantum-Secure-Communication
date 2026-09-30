from communication.participant import Participant
from communication.relay import CommunicationRelay


print("=" * 65)
print("STAGE 4B - BIDIRECTIONAL SECURE COMMUNICATION")
print("=" * 65)


# --------------------------------------------------
# Step 1: Create participants
# --------------------------------------------------

print("\n[1] Creating participants...")

alice = Participant("Alice")
bob = Participant("Bob")

print("    ✓ Alice created")
print("    ✓ Bob created")


# --------------------------------------------------
# Step 2: Generate keys
# --------------------------------------------------

print("\n[2] Generating cryptographic keys...")

alice.generate_keys()
bob.generate_keys()

print("    ✓ Alice ML-KEM-768 keys generated")
print("    ✓ Bob ML-KEM-768 keys generated")

print("    ✓ Alice ML-DSA-65 keys generated")
print("    ✓ Bob ML-DSA-65 keys generated")


# --------------------------------------------------
# Step 3: Exchange public signature keys
# --------------------------------------------------

print("\n[3] Exchanging public signature keys...")

alice.peer_signature_public_key = (
    bob.signature_public_key
)

bob.peer_signature_public_key = (
    alice.signature_public_key
)

print("    ✓ Alice received Bob's public signature key")
print("    ✓ Bob received Alice's public signature key")


# --------------------------------------------------
# Step 4: Establish shared session
# --------------------------------------------------

print("\n[4] Establishing secure session...")

kem_ciphertext = alice.create_session_with(
    bob
)

bob.accept_session(
    kem_ciphertext
)

print("    ✓ Alice encapsulated shared secret")
print("    ✓ Bob decapsulated shared secret")
print("    ✓ Both derived AES-256 session keys")


# --------------------------------------------------
# Step 5: Compare keys
# --------------------------------------------------

print("\n[5] Comparing session keys...")

if alice.session_key == bob.session_key:

    print("    ✓ Alice and Bob have the same session key")

else:

    print("    ✗ Session keys do not match")


# --------------------------------------------------
# Step 6: Create relay
# --------------------------------------------------

print("\n[6] Starting communication relay...")

relay = CommunicationRelay()

print("    ✓ Relay is ready")


# ==================================================
# ALICE → BOB
# ==================================================

print("\n" + "-" * 65)
print("DIRECTION 1: ALICE → BOB")
print("-" * 65)


alice_message = (
    "Hello Bob! Alice is sending a secure message."
)

print("\n[7] Alice sends message...")
print(f"    Plaintext: {alice_message}")


alice_packet = alice.send_message(
    bob,
    alice_message
)

print("    ✓ AES-256-GCM encryption completed")
print("    ✓ ML-DSA-65 signature created")


print("\n[8] Relay forwards Alice's packet...")

relay.send(alice_packet)

print("    ✓ Encrypted packet forwarded")


print("\n[9] Bob receives Alice's message...")

received_packet = relay.receive()

bob_message = bob.receive_message(
    received_packet
)

print(f"    Decrypted message: {bob_message}")
print("    ✓ AES-256-GCM decryption successful")
print("    ✓ Alice's ML-DSA-65 signature VALID")


# ==================================================
# BOB → ALICE
# ==================================================

print("\n" + "-" * 65)
print("DIRECTION 2: BOB → ALICE")
print("-" * 65)


bob_message_text = (
    "Hello Alice! Bob received your message securely."
)

print("\n[10] Bob sends message...")
print(f"    Plaintext: {bob_message_text}")


bob_packet = bob.send_message(
    alice,
    bob_message_text
)

print("    ✓ AES-256-GCM encryption completed")
print("    ✓ ML-DSA-65 signature created")


print("\n[11] Relay forwards Bob's packet...")

relay.send(bob_packet)

print("    ✓ Encrypted packet forwarded")


print("\n[12] Alice receives Bob's message...")

received_packet = relay.receive()

alice_message_received = alice.receive_message(
    received_packet
)

print(
    f"    Decrypted message: "
    f"{alice_message_received}"
)

print("    ✓ AES-256-GCM decryption successful")
print("    ✓ Bob's ML-DSA-65 signature VALID")


# --------------------------------------------------
# Final verification
# --------------------------------------------------

print("\n[13] Final verification...")

alice_to_bob_success = (
    bob_message == alice_message
)

bob_to_alice_success = (
    alice_message_received == bob_message_text
)

if alice_to_bob_success and bob_to_alice_success:

    print("    ✓ ALICE → BOB communication successful")
    print("    ✓ BOB → ALICE communication successful")
    print("    ✓ BIDIRECTIONAL SECURE COMMUNICATION SUCCESSFUL")

else:

    print("    ✗ Bidirectional communication failed")


print("\n" + "=" * 65)
print("STAGE 4B TEST COMPLETED")
print("=" * 65)