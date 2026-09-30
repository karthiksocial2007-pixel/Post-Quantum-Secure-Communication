import os
import threading

from cryptography.exceptions import InvalidTag
from flask import Blueprint, jsonify, render_template, request

from attacks.interception import InterceptionAttack
from attacks.replay import ReplayAttack
from attacks.tampering import TamperingAttack
from communication.participant import PacketRejected, Participant
from communication.relay import CommunicationRelay
from crypto.encryption import AESGCMEncryption

import dataclasses


api = Blueprint("api", __name__)

MAX_MESSAGE_LENGTH = 1000


# ============================================================
# DEMO STATE (in-memory, one session per server process)
# ============================================================

class DemoState:
    """Holds Alice, Bob, the relay and the packet used by the attacks."""

    def __init__(self):

        self.lock = threading.RLock()
        self.reset()

    def reset(self):

        with self.lock:

            self.alice = Participant("Alice")
            self.bob = Participant("Bob")

            self.alice.generate_keys()
            self.bob.generate_keys()

            # Exchange ML-DSA public keys (simplified PKI)
            self.alice.peer_signature_public_key = (
                self.bob.signature_public_key
            )
            self.bob.peer_signature_public_key = (
                self.alice.signature_public_key
            )

            # ML-KEM-768 session establishment
            kem_ciphertext = self.alice.create_session_with(self.bob)
            self.bob.accept_session(kem_ciphertext)

            self.relay = CommunicationRelay()

            # Original (unmodified) packets by ID, so an attack that swaps
            # the packet in transit never destroys the reference copy
            self.sent = {}

            # Last packet Receive & Verify processed (accepted or rejected)
            self.last_processed = None

            # Last packet that was ACCEPTED (used by the replay attack)
            self.last_received = None

            # message_id -> name of the attack that modified it in transit
            self.modified = {}

    def participant(self, name):

        return self.alice if name == "Alice" else self.bob

    def session_ok(self):

        return (
            self.alice.session_key is not None
            and self.alice.session_key == self.bob.session_key
        )


state = DemoState()


def _json_body():

    data = request.get_json(silent=True)

    return data if isinstance(data, dict) else None


def _no_packet(attack_name):

    return jsonify({
        "attack": attack_name,
        "status": "NO PACKET AVAILABLE",
        "detected": False,
        "protection": "Send a message first, then run the attack."
    }), 400


def _attack_target():
    """Return (original_packet, in_transit).

    Attacks aim at the packet Receive & Verify will process next. If
    nothing is waiting in the relay they fall back to the last packet
    that was already processed.
    """

    head = state.relay.peek()

    if head is not None:
        return state.sent.get(head.message_id, head), True

    return state.last_processed, False


def _next_step(in_flight):

    if in_flight:
        return (
            "The modified packet replaced the real one in transit. "
            "Click Receive & Verify: Bob will now REJECT it."
        )

    return (
        "No message is in transit (the last one was already processed), "
        "so the attack was tested on a captured copy. Send a new message "
        "and attack it BEFORE clicking Receive to see it rejected in "
        "transit."
    )


# ============================================================
# HOME / STATUS / RESET
# ============================================================

@api.route("/", methods=["GET"])
def home():

    return render_template("index.html")


@api.route("/api/status", methods=["GET"])
def status():

    with state.lock:

        head = state.relay.peek()

        return jsonify({
            "status": "Secure communication system is running",
            "alice": "ready",
            "bob": "ready",
            "session_established": state.session_ok(),
            "pending_messages": state.relay.pending(),
            "next_sender": head.sender if head else None,
            "next_receiver": head.receiver if head else None,
            "modified_by": (
                state.modified.get(head.message_id) if head else None
            ),
            "algorithms": {
                "kem": "ML-KEM-768",
                "kdf": "HKDF-SHA256",
                "aead": "AES-256-GCM",
                "signature": "ML-DSA-65"
            }
        })


@api.route("/api/reset", methods=["POST"])
def reset():

    state.reset()

    return jsonify({"status": "New ML-KEM session established"})


# ============================================================
# SEND MESSAGE
# ============================================================

@api.route("/api/message", methods=["POST"])
def send_message():

    data = _json_body()

    if data is None:
        return jsonify({"error": "JSON request body is required"}), 400

    sender = data.get("sender")
    message = data.get("message")

    if sender not in ("Alice", "Bob"):
        return jsonify({"error": "Sender must be Alice or Bob"}), 400

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message is required"}), 400

    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({
            "error": f"Message must be at most {MAX_MESSAGE_LENGTH} characters"
        }), 400

    try:

        with state.lock:

            receiver = "Bob" if sender == "Alice" else "Alice"

            packet = state.participant(sender).send_message(
                state.participant(receiver),
                message
            )

            state.relay.send(packet)
            state.sent[packet.message_id] = packet

        return jsonify({
            "status": "Message encrypted and signed",
            "sender": packet.sender,
            "receiver": packet.receiver,
            "message_id": packet.message_id,
            "timestamp": packet.timestamp,
            "nonce": packet.nonce.hex(),
            "ciphertext": packet.ciphertext.hex(),
            "signature": packet.signature.hex()
        })

    except Exception as error:

        return jsonify({
            "status": "Message creation failed",
            "error": str(error)
        }), 500


# ============================================================
# RECEIVE MESSAGE
# ============================================================

@api.route("/api/message/receive", methods=["POST"])
def receive_message():

    with state.lock:

        packet = state.relay.receive()

        if packet is None:
            return jsonify({"error": "No message available"}), 404

        original = state.sent.get(packet.message_id, packet)
        state.last_processed = original

        try:

            plaintext = state.participant(
                packet.receiver
            ).receive_message(packet)

            state.last_received = original

        except (PacketRejected, ValueError) as error:

            return jsonify({
                "status": "Message rejected",
                "error": str(error)
            }), 400

    return jsonify({
        "status": "Message successfully decrypted and verified",
        "sender": packet.sender,
        "receiver": packet.receiver,
        "message_id": packet.message_id,
        "message": plaintext,
        "signature_valid": True
    })


# ============================================================
# ATTACK 1 - CIPHERTEXT TAMPERING
# ============================================================

@api.route("/api/attack/tampering", methods=["POST"])
def attack_tampering():

    with state.lock:

        packet, _ = _attack_target()

        if packet is None:
            return _no_packet("Ciphertext Tampering")

        receiver = state.participant(packet.receiver)

        tampered = dataclasses.replace(
            packet,
            ciphertext=TamperingAttack.modify_ciphertext(packet.ciphertext)
        )

        # Man-in-the-middle: if the packet is still in transit, the
        # attacker really swaps it, so Receive & Verify will reject it.
        in_flight = state.relay.replace(packet.message_id, tampered)

        if in_flight:
            state.modified[packet.message_id] = "Ciphertext Tampering"

        try:
            receiver.decrypt_and_verify(tampered)

        except PacketRejected as error:

            return jsonify({
                "attack": "Ciphertext Tampering",
                "status": "ATTACK DETECTED",
                "detected": True,
                "in_flight": in_flight,
                "protection": (
                    "AES-256-GCM authentication rejected the modified "
                    "ciphertext"
                ),
                "next_step": _next_step(in_flight),
                "error": str(error)
            })

    return jsonify({
        "attack": "Ciphertext Tampering",
        "status": "ATTACK NOT DETECTED",
        "detected": False
    })


# ============================================================
# ATTACK 2 - MESSAGE MODIFICATION (ML-DSA)
# ============================================================
# An attacker who somehow holds the session key (for example a
# compromised endpoint) can re-encrypt a modified message and AES-GCM
# will accept it. Only the ML-DSA signature can catch this.

@api.route("/api/attack/signature", methods=["POST"])
def attack_signature():

    with state.lock:

        packet, _ = _attack_target()

        if packet is None:
            return _no_packet("Message Modification")

        receiver = state.participant(packet.receiver)

        plaintext = receiver.aes.decrypt(
            packet.nonce,
            packet.ciphertext,
            packet.aad()
        )

        nonce, ciphertext = receiver.aes.encrypt(
            plaintext + " [MODIFIED BY ATTACKER]",
            packet.aad()
        )

        forged = dataclasses.replace(
            packet,
            nonce=nonce,
            ciphertext=ciphertext
        )

        # Man-in-the-middle: replace the packet still in transit
        in_flight = state.relay.replace(packet.message_id, forged)

        if in_flight:
            state.modified[packet.message_id] = "Message Modification"

        try:
            receiver.decrypt_and_verify(forged)

        except PacketRejected as error:

            by_signature = "ML-DSA" in str(error)

            return jsonify({
                "attack": "Message Modification",
                "status": "ATTACK DETECTED",
                "detected": True,
                "in_flight": in_flight,
                "protection": (
                    "AES-GCM accepted the re-encrypted text, but "
                    "ML-DSA-65 signature verification rejected the "
                    "modified message"
                    if by_signature
                    else "The modified packet was rejected: " + str(error)
                ),
                "next_step": _next_step(in_flight),
                "error": str(error)
            })

    return jsonify({
        "attack": "Message Modification",
        "status": "ATTACK NOT DETECTED",
        "detected": False
    })


# ============================================================
# ATTACK 3 - REPLAY
# ============================================================

@api.route("/api/attack/replay", methods=["POST"])
def attack_replay():

    with state.lock:

        packet = state.last_received

        receiver = (
            state.participant(packet.receiver)
            if packet is not None else None
        )

        if (
            packet is None
            or packet.message_id not in receiver.received_message_ids
        ):

            return jsonify({
                "attack": "Replay Attack",
                "status": "RECEIVE MESSAGE FIRST",
                "detected": False,
                "protection": (
                    "Click Receive & Verify first. A replay is a second "
                    "delivery of a message that was already accepted."
                )
            }), 409

        results = []
        exact_reason = ""
        forged_reason = ""

        # 1) exact resend
        try:
            receiver.receive_message(ReplayAttack.resend(packet))
            exact_blocked = False

        except PacketRejected as error:
            exact_blocked = True
            exact_reason = str(error)
            results.append(exact_reason)

        # 2) resend with a forged message ID
        try:
            receiver.receive_message(
                ReplayAttack.resend_with_new_id(packet)
            )
            forged_blocked = False

        except PacketRejected as error:
            forged_blocked = True
            forged_reason = str(error)
            results.append(forged_reason)

    if exact_blocked and forged_blocked:

        return jsonify({
            "attack": "Replay Attack",
            "status": "ATTACK DETECTED",
            "detected": True,
            "protection": (
                (
                    "Duplicate message ID rejected. "
                    if "Replay attack detected" in exact_reason
                    else f"Exact resend rejected ({exact_reason}). "
                )
                + (
                    "A forged new ID was also rejected because the ID is "
                    "authenticated by AES-GCM"
                    if "AES-256-GCM" in forged_reason
                    else f"A forged new ID was also rejected ({forged_reason})"
                )
            ),
            "error": " | ".join(results)
        })

    return jsonify({
        "attack": "Replay Attack",
        "status": "ATTACK NOT DETECTED",
        "detected": False
    })


# ============================================================
# ATTACK 4 - WRONG SESSION KEY
# ============================================================

@api.route("/api/attack/wrong-key", methods=["POST"])
def attack_wrong_key():

    with state.lock:

        packet, _ = _attack_target()

        if packet is None:
            return _no_packet("Wrong Session Key")

        receiver = state.participant(packet.receiver)

        # Control: the real session key must work
        receiver.aes.decrypt(packet.nonce, packet.ciphertext, packet.aad())

    attacker_aes = AESGCMEncryption(os.urandom(32))

    try:
        attacker_aes.decrypt(
            packet.nonce,
            packet.ciphertext,
            packet.aad()
        )

    except InvalidTag:

        return jsonify({
            "attack": "Wrong Session Key",
            "status": "ATTACK DETECTED",
            "detected": True,
            "protection": (
                "AES-256-GCM rejected decryption with a different "
                "session key (the real key still decrypts it)"
            ),
            "next_step": (
                "Passive attack: the packet was not altered, so "
                "Receive & Verify will still succeed. That is correct."
            )
        })

    return jsonify({
        "attack": "Wrong Session Key",
        "status": "ATTACK NOT DETECTED",
        "detected": False
    })


# ============================================================
# ATTACK 5 - INTERCEPTION
# ============================================================

@api.route("/api/attack/interception", methods=["POST"])
def attack_interception():

    with state.lock:

        packet, _ = _attack_target()

        if packet is None:
            return _no_packet("Packet Interception")

        receiver = state.participant(packet.receiver)

        plaintext = receiver.aes.decrypt(
            packet.nonce,
            packet.ciphertext,
            packet.aad()
        )

    exposed = InterceptionAttack.plaintext_exposed(packet, plaintext)

    if exposed:

        return jsonify({
            "attack": "Packet Interception",
            "status": "PLAINTEXT VISIBLE",
            "detected": False,
            "protection": "Interception test failed"
        })

    return jsonify({
        "attack": "Packet Interception",
        "status": "INTERCEPTION PROTECTED",
        "detected": True,
        "protection": (
            "The captured packet holds AES-256-GCM ciphertext, not "
            "plaintext. Interception itself is not detected - it is "
            "made useless"
        ),
        "plaintext_visible": False
    })
