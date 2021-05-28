from network_details import *
from socket import *
import pickle
class Network:

    def __init__(self):
        self.client = socket(AF_INET,SOCK_STREAM)
        self.player=self.connect()
        print("Player assigned")

    def get_player(self):
        return self.player

    def connect(self):
        self.client.connect((ip,port))
        return pickle.loads(self.client.recv(1024))

    def send(self,obj):
        self.client.sendall(pickle.dumps(obj))
        return pickle.loads(self.client.recv(16384))

    def recv(self):
        return pickle.loads(self.client.recv(16384))
