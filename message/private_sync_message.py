from .private_message import PrivateMessage

class PrivateMessageSync(PrivateMessage):
    """
    Initialise un message brodacast avec :
        - l'estampille
        - le contenu
        - l'émetteur

    sender et msg_id sont requis uniquement pour la communication synchrone
    Ce message n'est pas système, donc impacte l'horloge Lamport
    """
    def __init__(self, dest, stamp, payload, sender):
        super().__init__(dest, stamp, payload, sender)