from threading import Lock, Thread
from time import sleep
from com import Com

import logging

class Process(Thread):
    
    def __init__(self):
        Thread.__init__(self)

        self.com = Com(logging.DEBUG)

        self.alive = True
        self.start()
    
    def run(self):
        self.com.init()
        self.myId = self.com.getMyId()
        name = "P" + str(self.myId)
        self.setName(name)

        loop = 0
        if self.getName() == "P1":
            sleep(2)
            self.com.sendToSync('coucou', 0)
        elif self.getName() == "P0":
            self.com.recevFromSync("", 0)

        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            if self.getName() == "P1":
                self.com.sendTo('cccc', 3)
            sleep(1)

                

    # def run(self):
    #     loop = 0
    #     msg = ""
    #     if self.getName() == "P2":
    #         self.com.sendTokenTo(0)

    #     while self.alive:
    #         print(self.getName() + " Loop: " + str(loop))
    #         sleep(1)

    #         if self.getName() == "P0":
    #             self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
    #             self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
    #             self.com.recevFromSync(msg, 2)
               
    #             self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                    
    #             self.com.synchronize()
                    
    #             self.com.requestSC()
    #             if self.com.mailbox.isEmpty():
    #                 print("Catched !")
    #                 self.com.broadcast("J'ai gagné !!!")
    #             else:
    #                 msg = self.com.mailbox.getMsg()
    #                 print(str(msg.getSender())+" à eu le jeton en premier")
    #             self.com.releaseSC()


    #         if self.getName() == "P1":
    #             if not self.com.mailbox.isEmpty():
    #                 self.com.mailbox.getMsg()
    #                 self.com.recevFromSync(msg, 0)

    #                 self.com.synchronize()
                    
    #                 self.com.requestSC()
    #                 if self.com.mailbox.isEmpty():
    #                     print("Catched !")
    #                     self.com.broadcast("J'ai gagné !!!")
    #                 else:
    #                     msg = self.com.mailbox.getMsg();
    #                     print(str(msg.getSender())+" à eu le jeton en premier")
    #                 self.com.releaseSC()
                    
    #         if self.getName() == "P2":
    #             self.com.recevFromSync(msg, 0)
    #             self.com.sendToSync("OK", 0)

    #             self.com.synchronize()
                    
    #             self.com.requestSC()
    #             if self.com.mailbox.isEmpty():
    #                 print("Catched !")
    #                 self.com.broadcast("J'ai gagné !!!")
    #             else:
    #                 msg = self.com.mailbox.getMsg()
    #                 print(str(msg.getSender())+" à eu le jeton en premier")
    #             self.com.releaseSC()
                

    #         loop+=1
    #     print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()