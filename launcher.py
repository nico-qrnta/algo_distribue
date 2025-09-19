from time import sleep
from process import Process

def launch(nbProcess, runningTime=10):
    processes = []

    for i in range(nbProcess):
        processes = processes + [Process()]
    
    sleep(runningTime)

    for p in processes:
        p.stop()

    for p in processes:
        p.waitStopped()

if __name__ == '__main__':

    #bus = EventBus.getInstance()
    
    launch(nbProcess=3, runningTime=10)

    #bus.stop()
