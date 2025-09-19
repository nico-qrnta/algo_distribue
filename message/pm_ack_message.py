from .ack_message import AckMessage

class PMAckMessage(AckMessage):
    def __init__(self, sender, dest):
        """
        Initialise un message d'accusé de réception avec :
            - l'émetteur
            - le destinataire
        """
        super().__init__(sender, dest)