from threading import Semaphore
from pyeventbus3.pyeventbus3 import *

from mailbox_queue import Mailbox
from message import BroadcastMessage, PrivateMessage

class Com():
    # -------- Initialisation --------

    """
    Instancie les différentes variables de Com
    """
    def __init__(self):
        # Horloge Lamport
        self.clock = 0
        self.clockMutex = Semaphore(1)

        # B.a.L
        self.mailbox = Mailbox()


    # -------- Numérotation automatique --------


    """
    Crée un id numéroté automatiquement pour le processus et le retourne
    Sortie => id du processus
    """
    def getMyId(self):
        NotImplemented


    # -------- Horloge Lamport --------


    """
    Incrémente l'horloge Lamport de façon protégée via un mutex
    """
    def incClock(self):
        self.clockMutex.acquire()
        self.clock += 1
        self.clockMutex.release()


    """
    Met à jour l'horloge Lamport de façon protégée via un mutex en se basant sur un message donné
    Entrée => l'estampille du message, un booléen indiquant la nature système du message
    """
    def incClockOnReceive(self, stamp, system):
        if not system:
            self.clockMutex.acquire()
            self.clock = max(stamp, self.clock) + 1
            self.clockMutex.release()


    # -------- Communications asynchrones --------


    """
    Récupère un message envoyé en broadcast de façon asynchrone
    Entrée => l'event contenant le message intercepté
    """
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        self.incClockOnReceive(event.stamp, event.system)
        self.mailbox.put(event)


    """
    Récupère un message privé envoyé de façon asynchrone
    Entrée => l'event contenant le message intercepté
    """
    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessage)
    def onPrivateMessage(self, event):
        self.incClockOnReceive(event.stamp, event.system)
        self.mailbox.put(event)


    """
    Envoie un message en broadcast de façon asynchrone
    Entrée => le message à envoyer
    """
    def broadcast(self, message):
        self.incClock()
        message = BroadcastMessage(self.clock, message)
        PyBus.Instance().post(message)


    """
    Envoie un message privé à un destinataire de façon asynchrone
    Entrée => le destinataire, le message à envoyer
    """
    def sendTo(self, to, message):
        self.incClock()
        message = PrivateMessage(to, self.clock, message)
        PyBus.Instance().post(message)