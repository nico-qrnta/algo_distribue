from .message import Message

class PrivateMessageId():
    def __init__(self, id, dest):
        """
        Initialise un message privé avec :
            - l'identifiant
            - le destinataire
        """
        self.id = id
        self.dest = dest