from .message import Message

class BroadcastMessageSync(Message):
    """
    Initialise un message brodacast avec :
        - l'estampille
        - le contenu
        - l'émetteur
        - l'id du message
        - un booléen indiquant la nature système du message.

    sender et msg_id sont requis uniquement pour la communication synchrone
    Ce message n'est pas système, donc impacte l'horloge Lamport
    """
    def __init__(self, stamp, payload, sender=None):
        super().__init__(stamp, payload, sender, system=False)