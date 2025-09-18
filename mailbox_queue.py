from queue import Queue

class Mailbox():
    """
    Initialise une B.a.L vide
    """
    def __init__(self):
        self.queue = Queue()


    """
    Retourne True si la B.a.L est vide, False sinon
    Sortie => État de remplissage de la B.a.L
    """
    def isEmpty(self):
        return self.queue.empty()


    """
    Récupère et supprime le premier message
    Sortie => message
    """
    def getMsg(self):
        return self.queue.get()


    """
    Ajoute un message
    Entrée => message
    """
    def add(self, payload):
        self.queue.put(payload)