from message import Message

class AckMessage(Message):
    def __init__(self, sender, msg_id):
        super().__init__(0, payload=None, sender=sender, msg_id=msg_id, system=True)