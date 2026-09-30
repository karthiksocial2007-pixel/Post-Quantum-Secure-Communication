# Post-Quantum Secure Communication Framework

An academic PBL demonstration of a post-quantum secure messaging pipeline
between two participants, Alice and Bob.

## Cryptographic building blocks

| Component     | Role                                              |
|----------------|---------------------------------------------------|
| ML-KEM-768     | Post-quantum key establishment                    |
| HKDF-SHA256    | Derives the AES-256 session key                   |
| AES-256-GCM    | Authenticated encryption of the message           |
| ML-DSA-65      | Post-quantum digital signature over the message   |

The packet header (sender, receiver, timestamp, message ID) is bound in as
AES-GCM associated data and is also covered by the ML-DSA signature, so it
cannot be altered or replayed with a new ID without detection.

## Setup

```powershell
cd PostQuantumSecureCommunication
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000

## Using the dashboard

1. **Send** a message (choose Alice or Bob as sender).
2. **Attack** (optional) - run an attack while the message is still in the relay.
   Attacks 01 and 02 really modify the packet in transit; use the
   **Receive & Verify now** button inside the attack card to see the receiver reject it.
3. **Receive** - Bob (or Alice) decrypts and verifies. The sticky bar at the top
   shows the relay state and whether the packet was modified; the
   **Activity** button (bottom right) keeps a log of every action.

## Running the tests

```powershell
pytest -q test_web_attacks.py
```

The other `test_*.py` files are stage demo scripts: run each one with
`python test_name.py` (they print step-by-step output and are not pytest tests).

## Project limitations

This is a demonstration framework, not a production messenger:

- The relay and session state are in-memory only (no database).
- There is no login system; ML-DSA public-key exchange is simplified (no PKI).
- The ML-KEM handshake itself is not authenticated in this demo.
- Packet interception is made useless by encryption, not "detected" as an event.
