from .ack_message import AckMessage

class PMAckMessage(AckMessage):
    def __init__(self, sender, dest):
        super().__init__(sender, dest)