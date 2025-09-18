class Message():
    """
    Initialise un message avec :
        - l'estampille
        - le contenu
        - l'émetteur
        - l'id du message
        - un booléen indiquant la nature système du message.
    """
    def __init__(self, stamp, payload, sender, msg_id, system):
        self.stamp = stamp
        self.payload = payload
        self.sender = sender
        self.msg_id = msg_id
        self.system = system