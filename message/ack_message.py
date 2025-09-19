class AckMessage():
    def __init__(self, sender, dest):
        """
        Initialise un message d'accusé de réception avec :
            - l'émetteur
            - le destinataire
        """
        self.dest = dest
        self.sender = sender