from queue import Queue

class Mailbox():
    def __init__(self):
        """
        Initialise une B.a.L vide
        """
        self.queue = Queue()


    def isEmpty(self):
        """
        Retourne True si la B.a.L est vide, False sinon
        Sortie => État de remplissage de la B.a.L
        """
        return self.queue.empty()


    def getMsg(self):
        """
        Récupère et supprime le premier message
        Sortie => message
        """
        return self.queue.get()


    def add(self, payload):
        """
        Ajoute un message
        Entrée => message
        """
        self.queue.put(payload)