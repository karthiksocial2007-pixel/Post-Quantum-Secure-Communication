import threading


class CommunicationRelay:
    """In-memory FIFO channel between the participants (demo only)."""

    def __init__(self):

        self.messages = []
        self._lock = threading.Lock()

    def send(self, secure_message):

        with self._lock:
            self.messages.append(secure_message)

    def receive(self):

        with self._lock:

            if not self.messages:
                return None

            return self.messages.pop(0)

    def pending(self):

        with self._lock:
            return len(self.messages)

    def replace(self, message_id, new_message):
        """Man-in-the-middle hook: swap a packet that is still in transit.

        Returns True if the packet was still queued (i.e. not yet received).
        """

        with self._lock:

            for index, queued in enumerate(self.messages):

                if queued.message_id == message_id:
                    self.messages[index] = new_message
                    return True

            return False

    def peek(self):
        """Packet that Receive & Verify will process next (or None)."""

        with self._lock:
            return self.messages[0] if self.messages else None
