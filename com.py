from threading import Lock
from pyeventbus3.pyeventbus3 import *

from mailbox_queue import Mailbox
from message import BroadcastMessage, PrivateMessage, TokenSC, SynchronizeEvent
from status import Status

import threading
import logging

class Com():
    # -------- Initialisation --------

    """
    Instancie les différentes variables de Com
    """
    def __init__(self, myId, log_level=logging.INFO):
        # Horloge Lamport
        self.clock = 0
        self.clockMutex = Lock()

        # B.a.L
        self.mailbox = Mailbox()
        
        # Section critique
        self.status = Status.NULL
        self.sc_semaphore = threading.Semaphore(0)
        self.finished_sc_semaphore = threading.Semaphore(0)

        #synchronize
        self.synchronizedProcess = []
        self.synchro_semaphore = threading.Semaphore(0)

        self.myId = myId

        self.logger = setup_logger(log_level)
        PyBus.Instance().register(self, self)


    # -------- Numérotation automatique --------

    """
    Crée un id numéroté automatiquement pour le processus et le retourne
    Sortie => id du processus
    """
    def getMyId(self):
        NotImplemented

    def getNbProcess(self):
        return 3

    # -------- Horloge Lamport --------


    """
    Incrémente l'horloge Lamport de façon protégée via un mutex
    """
    def incClock(self):
        self.clockMutex.acquire()
        self.clock += 1
        self.logger.debug(f"P{self.myId} -> Horloge incrémentée: {self.clock}")
        self.clockMutex.release()


    """
    Met à jour l'horloge Lamport de façon protégée via un mutex en se basant sur un message donné
    Entrée => l'estampille du message, un booléen indiquant la nature système du message
    """
    def incClockOnReceive(self, stamp, system):
        if not system:
            self.clockMutex.acquire()
            self.clock = max(stamp, self.clock) + 1
            self.logger.debug(f"P{self.myId} -> Horloge mise à jour sur reception: {self.clock}")
            self.clockMutex.release()

        
    # -------- Section critique --------


    """
    Bloque le processus jusqu'à obtention du jeton de section critique
    """
    def requestSC(self):
        self.logger.info(f"P{self.myId} -> Demande SC")
        self.status = Status.REQUEST
        self.sc_semaphore.acquire()
        self.status = Status.SECTION_CRITIQUE
        self.logger.info(f"P{self.myId} -> Entrée SC")

    """
    Libère le jeton de section critique
    """
    def releaseSC(self):
        if self.status != Status.SECTION_CRITIQUE:
            return

        self.logger.info(f"P{self.myId} -> Sortie SC")
        self.status = Status.NULL
        self.finished_sc_semaphore.release()

    @subscribe(threadMode = Mode.PARALLEL, onEvent=TokenSC)
    def onToken(self, event):
        self.logger.debug(f"P{self.myId} -> Token reçu pour {event.to}")
        if event.to != self.myId:
            return

        if self.status == Status.REQUEST:
            self.logger.info(f"P{self.myId} -> Je garde le token pour entrer en SC")
            self.sc_semaphore.release()
            self.finished_sc_semaphore.acquire()
        
        self.logger.debug(f"P{self.myId} -> Je passe le token")
        self.sendTokenTo((self.myId + 1) % self.getNbProcess())

    def sendTokenTo(self, to):
        self.logger.debug(f"P{self.myId} -> J'envoie le token à {to}")
        token = TokenSC(to)
        time.sleep(0.5)
        PyBus.Instance().post(token)

    # -------- Synchronisation --------
    """
    Bloque le processus jusqu'à ce que tous les autres processus aient appelé cette méthode
    """
    def synchronize(self):
        self.logger.info(f"P{self.myId} -> Attente synchronize")
        synchronizeEvent = SynchronizeEvent(self.myId)
        PyBus.Instance().post(synchronizeEvent)
        
        self.synchro_semaphore.acquire()
        self.logger.info(f"P{self.myId} -> Fin synchronize")


    @subscribe(threadMode = Mode.PARALLEL, onEvent=SynchronizeEvent)
    def onSynchronizeEvent(self, event):
        self.synchronizedProcess.append(event.source)

        if len(self.synchronizedProcess) == self.getNbProcess():
            self.synchro_semaphore.release()


    # -------- Communication asynchrone --------
    """
    Récupère un message envoyé en broadcast de façon asynchrone
    Entrée => l'event contenant le message intercepté
    """
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        self.incClockOnReceive(event.stamp, event.system)
        self.mailbox.add(event)


    """
    Récupère un message privé envoyé de façon asynchrone
    Entrée => l'event contenant le message intercepté
    """
    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessage)
    def onPrivateMessage(self, event):
        if event.to != self.myId:
           return

        self.logger.debug(f"P{self.myId} -> Message privé reçu de {event.to}: {event.message}")
        self.incClockOnReceive(event.stamp, event.system)
        self.mailbox.add(event)


    """
    Envoie un message en broadcast de façon asynchrone
    Entrée => le message à envoyer
    """
    def broadcast(self, message):
        self.incClock()
        message = BroadcastMessage(self.clock, message)
        self.logger.debug(f"P{self.myId} -> Envoi broadcast: {message}")
        PyBus.Instance().post(message)


    """
    Envoie un message privé à un destinataire de façon asynchrone
    Entrée => le destinataire, le message à envoyer
    """
    def sendTo(self, message, to):
        self.incClock()
        message = PrivateMessage(to, self.clock, message)
        self.logger.debug(f"P{self.myId} -> Envoi privé à {to}: {message}")
        PyBus.Instance().post(message)

    # -------- Communication synchrone --------

    """
    Si le processus est l'émetteur, envoie un message en broadcast de façon asynchrone, sinon reçoit le message
    Entrée => le message à envoyer ou recevoir, l'expéditeur
    """
    def broadcastSync(self, message, sender):
        NotImplemented

    
    """
    Envoie un message privé à un destinataire de façon synchrone et bloque jusqu'à la réception du message
    Entrée => le message à envoyer, le destinataire
    """
    
    def sendToSync(self, message, to):
        NotImplemented


    """
    Récupère un message privé envoyé de façon synchrone et bloque jusqu'à l'envoi du message
    Entrée => l'event contenant le message intercepté
    """
    def recevFromSync(self, message, sender):
        NotImplemented









# --- LOGGER ---

def setup_logger(level=logging.INFO):
    logger = logging.getLogger("ComLogger")
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)

    if not logger.handlers:  # éviter duplication
        logger.addHandler(ch)

    return logger