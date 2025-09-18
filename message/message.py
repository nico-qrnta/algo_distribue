class Message():

    def __init__(self, stamp, payload, sender, msg_id, system):
        self.stamp = stamp
        self.payload = payload
        self.sender = sender
        self.msg_id = msg_id
        self.system = system