from .message import Message

class BroadcastMessage(Message):
    def __init__(self, stamp, payload, sender=None):
        """
        Initialise un message brodacast avec :
            - l'estampille
            - le contenu
            - l'émetteur

        sender et msg_id sont requis uniquement pour la communication synchrone
        Ce message n'est pas système, donc impacte l'horloge Lamport
        """
        super().__init__(stamp, payload, sender)