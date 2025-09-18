from threading import Semaphore
from pyeventbus3.pyeventbus3 import *

from mailbox_queue import Mailbox
from message import BroadcastMessage, PrivateMessage

class Com():    

    def __init__(self):
        self.clock = 0
        self.clockMutex = Semaphore(1)
        self.mailbox = Mailbox()
        self.processList = []
        self.processMutex = Semaphore(1)

    def getMyId(self):
        self.processMutex.acquire()
        newId = len(self.processList)
        self.processList.append(newId)
        self.processMutex.release()
        return newId

    def incClock(self):
        self.clockMutex.acquire()
        self.clock += 1
        self.clockMutex.release()

    def incClockOnReceive(self, stamp):
        self.clockMutex.acquire()
        self.clock = max(stamp, self.clock) + 1
        self.clockMutex.release()

    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        self.incClockOnReceive(event.stamp)
        self.mailbox.put(event)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=PrivateMessage)
    def onPrivateMessage(self, event):
        self.incClockOnReceive(event.stamp)
        self.mailbox.put(event)

    def broadcast(self, message):
        self.inc_clock()

        message = BroadcastMessage(self.clock, message)
        PyBus.Instance().post(message)

    def sendTo(self, to, message):
        self.inc_clock()

        message = PrivateMessage(to, self.clock, message)
        PyBus.Instance().post(message)