import dataclasses
import uuid


class ReplayAttack:

    @staticmethod
    def resend(packet):
        """Attacker re-sends the captured packet unchanged."""

        return packet

    @staticmethod
    def resend_with_new_id(packet):
        """Attacker re-sends the packet with a fresh message ID to dodge
        the seen-ID list. The ID is authenticated, so this must fail."""

        return dataclasses.replace(
            packet,
            message_id=str(uuid.uuid4())
        )
