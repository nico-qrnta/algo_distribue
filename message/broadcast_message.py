from .message import Message

class BroadcastMessage(Message):
    def __init__(self, stamp, payload, sender=None):
        """
        Initialise un message brodacast avec :
            - l'estampille
            - le contenu
            - l'émetteur

        sender est requis uniquement pour la communication synchrone
        """
        super().__init__(stamp, payload, sender)