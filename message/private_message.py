from message import Message

class PrivateMessage(Message):
    def __init__(self, to, stamp, payload, sender=None, msg_id=None):
        super().__init__(stamp, payload, sender, msg_id, system=False)
        self.to = to