"""Web dashboard attack tests (run with: pytest -q test_web_attacks.py)."""

import pytest

from app import create_app


@pytest.fixture()
def client():
    client = create_app().test_client()
    client.post("/api/reset")
    return client


def send(client, sender="Alice", message="hello bob"):
    return client.post("/api/message", json={"sender": sender, "message": message})


def receive(client):
    return client.post("/api/message/receive")


def attack(client, name):
    return client.post(f"/api/attack/{name}")


@pytest.mark.parametrize("sender", ["Alice", "Bob"])
@pytest.mark.parametrize("name,error", [
    ("tampering", "AES-256-GCM authentication failed"),
    ("signature", "Invalid ML-DSA signature"),
])
def test_active_attack_is_rejected_on_receive(client, sender, name, error):
    send(client, sender)
    result = attack(client, name).get_json()
    assert result["status"] == "ATTACK DETECTED" and result["in_flight"]

    response = receive(client)
    assert response.status_code == 400
    assert error in response.get_json()["error"]


@pytest.mark.parametrize("message", ["a", "0", "e", "cafe", "hello bob", "x" * 1000])
def test_interception_has_no_false_positives(client, message):
    send(client, message=message)
    assert attack(client, "interception").get_json()["status"] == "INTERCEPTION PROTECTED"


def test_passive_attacks_do_not_break_delivery(client):
    send(client)
    attack(client, "wrong-key")
    attack(client, "interception")
    response = receive(client)
    assert response.status_code == 200
    assert response.get_json()["message"] == "hello bob"


def test_replay_needs_a_received_message_then_is_detected(client):
    assert attack(client, "replay").status_code == 409
    send(client)
    assert attack(client, "replay").status_code == 409
    receive(client)
    assert attack(client, "replay").get_json()["status"] == "ATTACK DETECTED"


def test_attack_targets_next_message_in_queue(client):
    send(client, message="first")
    send(client, message="second")
    attack(client, "tampering")
    assert receive(client).status_code == 400
    assert receive(client).get_json()["message"] == "second"


def test_repeated_attacks_never_crash(client):
    send(client)
    for name in ["tampering", "signature", "tampering", "wrong-key", "interception"]:
        assert attack(client, name).status_code == 200


def test_attacks_without_packet_return_400(client):
    for name in ["tampering", "signature", "wrong-key", "interception"]:
        assert attack(client, name).status_code == 400
