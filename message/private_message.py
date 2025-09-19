from .message import Message

class PrivateMessage(Message):
    def __init__(self, to, stamp, payload, sender=None):
        """
        Initialise un message privé avec :
            - le destinataire
            - l'estampille
            - le contenu
            - l'émetteur

        sender et msg_id sont requis uniquement pour la communication synchrone
        Ce message n'est pas système, donc impacte l'horloge Lamport
        """
        super().__init__(stamp, payload, sender)
        self.to = to