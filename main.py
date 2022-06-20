from time import sleep
from kazoo.client import KazooClient
from kazoo.protocol.states import EventType
import subprocess

zk = KazooClient(hosts='127.0.0.1:2181')
p = None


def open_close_paint(event):
    if event.type == EventType.CREATED:
        counter = zk.Counter("/int")
        counter -= counter.value
        print("Current number of descendants: " + str(counter.value))
        print("open Paint")
        global p
        p = subprocess.Popen(["mspaint"])
        zk.exists("/z", watch=open_close_paint)
    elif event.type == EventType.DELETED:
        print("close Paint")
        p.kill()


def display_descendant_counter(event):
    if event.path != "/z":
        counter = zk.Counter("/int")
        if event.type == EventType.CREATED:
            counter += 1
        elif event.type == EventType.DELETED:
            counter -= 1
        print("Current number of descendants: " + str(counter.value))
        if event.type != EventType.DELETED:
            zk.exists(event.path, watch=display_descendant_counter)


def display_tree(path="/z", indent=0):
    print("    "*indent+path)
    for child in zk.get_children(path):
        display_tree(path+"/"+child, indent+1)


def main():
    zk.start()
    while True:
        command = input()
        if command == "x":
            if zk.exists("/z"):
                zk.delete("/z", recursive=True)
                sleep(2)
            zk.stop()
            return
        command = command.split()
        if command[0] == "create":
            if command[1] == "/z":
                zk.exists("/z", watch=open_close_paint)
            zk.exists(command[1], watch=display_descendant_counter)
            zk.create(command[1])
        elif command[0] == "delete":
            zk.delete(command[1], recursive=True)
        elif command[0] == "tree":
            display_tree()


if __name__ == "__main__":
    main()
