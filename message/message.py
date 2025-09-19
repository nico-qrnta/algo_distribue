class Message():
    """
    Initialise un message avec :
        - l'estampille
        - le contenu
        - l'émetteur
    """
    def __init__(self, stamp, payload, sender):
        self.stamp = stamp
        self.payload = payload
        self.sender = sender
