class Message():
    def __init__(self, stamp, payload, sender):
        """
        Initialise un message avec :
            - l'estampille
            - le contenu
            - l'émetteur
        """
        self.stamp = stamp
        self.payload = payload
        self.sender = sender

    def getSender(self):
        return self.sender