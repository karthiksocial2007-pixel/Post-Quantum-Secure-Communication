from communication.message import SecureMessage


message = SecureMessage(
    sender="Alice",
    receiver="Bob",
    nonce=b"example_nonce",
    ciphertext=b"example_ciphertext",
    signature=b"example_signature",
    timestamp=SecureMessage.create_timestamp(),
    message_id=SecureMessage.create_message_id()
)


print("=" * 50)
print("SECURE MESSAGE TEST")
print("=" * 50)

print("\nSender:", message.sender)
print("Receiver:", message.receiver)
print("Timestamp:", message.timestamp)

print("\nMessage dictionary:")
print(f"Message ID: {message.message_id}")
print(message.to_dict())

print("\n✓ SecureMessage structure working")