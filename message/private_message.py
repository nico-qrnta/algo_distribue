from .message import Message

class PrivateMessage(Message):
    def __init__(self, to, stamp, payload, sender=None):
        """
        Initialise un message privé avec :
            - le destinataire
            - l'estampille
            - le contenu
            - l'émetteur

        sender est requis uniquement pour la communication synchrone
        """
        super().__init__(stamp, payload, sender)
        self.to = to