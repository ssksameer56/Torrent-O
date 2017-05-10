#Handle the Torrent Client for the user
import sys
from twisted.internet import reactor
import CoreTCP
import FileReadWrite
import MessagesAndHandshakes
import Metainfo
import RequestManager
import Tracker
import TorrentGUI
from Torrent import Torrent

class Client(object):
    'Class to handle a torrent object and its interface'
    def initTorrent(self, addr, reactor):
        'Initializes all the variables'
        self.torrent = Torrent(addr, reactor)

if __name__ == "__main__":
    client     = Client()
    client_gui = TorrentGUI(client)
    client.torrent.torrentStart()
