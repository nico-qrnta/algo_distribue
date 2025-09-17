from queue import Queue

class Mailbox():
    def __init__(self):
        self.queue = Queue()

    def isEmpty(self):
        return self.queue.empty()

    def getMsg(self):
        return self.queue.get()

    def add(self, payload):
        self.queue.put(payload)