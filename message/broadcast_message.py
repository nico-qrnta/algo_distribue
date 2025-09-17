from message import Message

class BroadcastMessage(Message):
    def __init__(self, stamp, payload):
        super().__init__(stamp, payload)