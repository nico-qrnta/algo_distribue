from .private_message import PrivateMessage

class PrivateMessageSync(PrivateMessage):
    def __init__(self, dest, stamp, payload, sender):
        """
        Initialise un message brodacast avec :
            - l'estampille
            - le contenu
            - l'émetteur

        sender est requis uniquement pour la communication synchrone
        """
        super().__init__(dest, stamp, payload, sender)