from message import Message

class PrivateMessage(Message):
    def __init__(self, to, stamp, payload):
        super().__init__(stamp, payload)
        self.to = to