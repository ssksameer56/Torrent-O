#Handle the Torrent Client for the user
import sys
from twisted.internet import reactor
import CoreTCP
import FileReadWrite
import MessagesAndHandshakes
import Metainfo
import RequestManager
import Tracker
from Torrent import Torrent

class Client(object):
    'Class to handle a torrent object and its interface'
    def __init__(self, addr, reactor):
        'Initializes all the variables'
        self.torrent = Torrent(addr, reactor)

if __name__ == "__main__":
    print 1
    client = Client(sys.argv[1], reactor)
    client.torrent.torrentStart()
