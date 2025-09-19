from threading import Lock
from pyeventbus3.pyeventbus3 import *

from mailbox_queue import Mailbox
from message import AckMessage, PrivateMessageId, BroadcastId, PMAckMessage, PrivateMessageSync, BroadcastMessage, PrivateMessage, TokenSC, SynchronizeEvent, BroadcastMessageSync
from status import Status

import threading
import logging
import random
import time

class Com():
    # -------- Initialisation --------

    def __init__(self, log_level=logging.INFO):
        """
        Instancie les différentes variables de Com
        """
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

        #broadcast synchrone
        self.broadcast_sync = threading.Semaphore(0)
        self.acked_broadcast_sync = []
        self.ack_broadcast_sync = threading.Semaphore(0)

        #private message synchrone
        self.pm_sync = threading.Semaphore(0)
        self.ack_pm_sync = threading.Semaphore(0)

        self.logger = setup_logger(log_level)
        PyBus.Instance().register(self, self)

        #numérotation automatique
        self.ids = []
        self.myId = None
        self.myUniqueId = None


    def init(self):
        time.sleep(4)
        self.initializeId()

    # -------- Numérotation automatique --------
    def getMyId(self):
        """
        Crée un id numéroté automatiquement pour le processus et le retourne
        Sortie => id du processus
        """
        return self.myId

    def initializeId(self):
        self.myUniqueId = random.randint(0, 10**18)
        self.ids.append(self.myUniqueId)
        
        message = BroadcastId(self.myUniqueId)
        PyBus.Instance().post(message)

        time.sleep(1)
        self.logger.info(f"P{self.myId} -> Emission de mon ID : {self.myUniqueId}")

    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastId)
    def onBroadcastId(self, event):
        """
        """
        if self.myUniqueId == event.id:
            return

        if event.id in self.ids:
            return

        self.ids.append(event.id)
        self.ids.sort()

        if self.myUniqueId != None :
            self.myId = self.ids.index(self.myUniqueId)
            message = PrivateMessageId(self.myUniqueId, event.id)
            PyBus.Instance().post(message)

    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessageId)
    def OnPrivateMessageId(self, event):
        """
        """
        if self.myUniqueId != event.dest:
            return

        self.ids.append(event.id)
        self.ids.sort()
        self.logger.debug(f"P{self.myId} -> Reception de ID : {event.id}")

        if self.myId != None :
            self.myId = self.ids.index(self.myUniqueId)

    def getNbProcess(self):
        """
        """
        return len(self.ids)
    
    # -------- Horloge Lamport --------

    def incClock(self):
        """
        Incrémente l'horloge Lamport de façon protégée via un mutex
        """
        self.clockMutex.acquire()
        self.clock += 1
        self.logger.debug(f"P{self.myId} -> Horloge incrémentée: {self.clock}")
        self.clockMutex.release()


    def incClockOnReceive(self, stamp):
        """
        Met à jour l'horloge Lamport de façon protégée via un mutex en se basant sur un message donné
        Entrée => l'estampille du message
        """
        self.clockMutex.acquire()
        self.clock = max(stamp, self.clock) + 1
        self.logger.debug(f"P{self.myId} -> Horloge mise à jour sur reception: {self.clock}")
        self.clockMutex.release()

        
    # -------- Section critique --------


    def requestSC(self):
        """
        Bloque le processus jusqu'à obtention du jeton de section critique
        """
        self.logger.info(f"P{self.myId} -> Demande SC")
        self.status = Status.REQUEST
        self.sc_semaphore.acquire()
        self.status = Status.SECTION_CRITIQUE
        self.logger.info(f"P{self.myId} -> Entrée SC")


    def releaseSC(self):
        """
        Libère le jeton de section critique
        """
        if self.status != Status.SECTION_CRITIQUE:
            return

        self.logger.info(f"P{self.myId} -> Sortie SC")
        self.status = Status.NULL
        self.finished_sc_semaphore.release()


    @subscribe(threadMode = Mode.PARALLEL, onEvent=TokenSC)
    def onToken(self, event):
        """
        """
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
        """
        """
        self.logger.debug(f"P{self.myId} -> J'envoie le token à {to}")
        token = TokenSC(to)
        time.sleep(0.5)
        PyBus.Instance().post(token)


    # -------- Synchronisation --------


    def synchronize(self):
        """
        Bloque le processus jusqu'à ce que tous les autres processus aient appelé cette méthode
        """
        self.logger.info(f"P{self.myId} -> Attente synchronize")
        synchronizeEvent = SynchronizeEvent(self.myId)
        PyBus.Instance().post(synchronizeEvent)
        
        self.synchro_semaphore.acquire()
        self.logger.info(f"P{self.myId} -> Fin synchronize")


    @subscribe(threadMode = Mode.PARALLEL, onEvent=SynchronizeEvent)
    def onSynchronizeEvent(self, event):
        """
        """
        self.synchronizedProcess.append(event.source)

        if len(self.synchronizedProcess) == self.getNbProcess():
            self.synchronizedProcess = []
            self.synchro_semaphore.release()


    # -------- Communication asynchrone --------


    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
        Récupère un message envoyé en broadcast de façon asynchrone
        Entrée => l'event contenant le message intercepté
        """
        self.incClockOnReceive(event.stamp)
        self.mailbox.add(event)


    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessage)
    def onPrivateMessage(self, event):
        """
        Récupère un message privé envoyé de façon asynchrone
        Entrée => l'event contenant le message intercepté
        """
        if event.to != self.myId:
           return

        self.logger.debug(f"P{self.myId} -> Message privé reçu de {event.sender}: {event.payload}")
        self.incClockOnReceive(event.stamp)
        self.mailbox.add(event)


    def broadcast(self, message):
        """
        Envoie un message en broadcast de façon asynchrone
        Entrée => le message à envoyer
        """
        self.incClock()
        message = BroadcastMessage(self.clock, message)
        self.logger.debug(f"P{self.myId} -> Envoi broadcast: {message.payload}")
        PyBus.Instance().post(message)


    def sendTo(self, message, to):
        """
        Envoie un message privé à un destinataire de façon asynchrone
        Entrée => le destinataire, le message à envoyer
        """
        self.incClock()
        message = PrivateMessage(to, self.clock, message)
        self.logger.debug(f"P{self.myId} -> Envoi privé à {to}: {message.payload}")
        PyBus.Instance().post(message)


    # -------- Communication synchrone --------


    def broadcastSync(self, message = None, sender = None):
        """
        Si le processus est l'émetteur, envoie un message en broadcast de façon asynchrone, sinon reçoit le message
        Entrée => le message à envoyer ou recevoir, l'expéditeur
        """
        if self.myId == sender:
            self.incClock()
            message = BroadcastMessageSync(self.clock, message, sender)
            PyBus.Instance().post(message)
            self.logger.info(f"P{self.myId} -> Envoi broadcast synchrone")
            self.ack_broadcast_sync.acquire()
        else:
            self.logger.info(f"P{self.myId} -> Attente broadcast synchrone")
            self.broadcast_sync.acquire()


    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcastSync(self, event):
        """
        """
        if event.sender == self.myId:
            return

        self.incClockOnReceive(event.stamp)
        self.sendAckTo(event.sender)
        self.logger.info(f"P{self.myId} -> A reçu broadcast synchrone : {event.payload}")


    def sendAckTo(self, dest):
        """
        """
        ack = AckMessage(self.myId, dest)
        PyBus.Instance().post(ack)
        self.broadcast_sync.release()
        
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=AckMessage)
    def onAck(self, event):
        """
        """
        if event.dest != self.myId:
            return
        
        self.logger.debug(f"P{self.myId} -> A reçu ACK : {event.payload}")
        self.acked_broadcast_sync.append(event.sender)

        if len(self.acked_broadcast_sync) == self.getNbProcess() - 1:
            self.acked_broadcast_sync = []
            self.ack_broadcast_sync.release()


    def sendToSync(self, message, to):
        """
        Envoie un message privé à un destinataire de façon synchrone et bloque jusqu'à la réception du message
        Entrée => le message à envoyer, le destinataire
        """    
        self.logger.info(f"P{self.myId} -> Envoi message privé synchrone")
        self.incClock()
        message = PrivateMessageSync(to, self.clock, message, self.myId)
        PyBus.Instance().post(message)
        self.ack_pm_sync.acquire()


    def recevFromSync(self, message, sender):
        """
        Récupère un message privé envoyé de façon synchrone et bloque jusqu'à l'envoi du message
        Entrée => l'event contenant le message intercepté
        """
        self.logger.info(f"P{self.myId} -> Attente message privé synchrone")
        self.pm_sync.acquire()


    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessageSync)
    def onPrivateMessageSync(self, event):
        """
        """
        if self.myId != event.to:
            return

        self.logger.debug(f"P{self.myId} ->  Message privé reçu de {event.to}: {event.payload}")
        self.sendAckPMTo(event.sender)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=PMAckMessage)
    def onPMAck(self, event):
        if event.dest != self.myId:
            return
        
        self.logger.info(f"P{self.myId} -> A reçu ACK message privé")
        self.ack_pm_sync.release()
        

    def sendAckPMTo(self, dest):
        """
        """
        ack = PMAckMessage(self.myId, dest)
        PyBus.Instance().post(ack)
        self.pm_sync.release()
        
# -------- LOGGER-----------


def setup_logger(level=logging.INFO):
    logger = logging.getLogger("ComLogger")
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)

    return logger