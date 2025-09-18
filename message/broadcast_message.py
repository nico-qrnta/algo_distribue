from message import Message

class BroadcastMessage(Message):
    def __init__(self, stamp, payload, sender=None, msg_id=None):
        super().__init__(stamp, payload, sender, msg_id, system=False)