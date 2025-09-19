from .message import Message

class AckMessage(Message):
    """
    Initialise un message avec :
        - l'estampille
        - le contenu
        - l'émetteur
        - un booléen indiquant la nature système du message.

    L'estampille est mise à 0 pour ne pas impacter l'horloge
    Le contenu est vide car ce message n'a pas pour but de transférer un contenu
    Ce message est système, donc n'impacte pas l'horloge Lamport
    """
    def __init__(self, sender, dest):
        super().__init__(0, payload=None, sender=sender, system=True)
        self.dest = dest