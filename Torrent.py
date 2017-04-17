#Class to handle all aspects of torrent
import struct
import socket
import sys
from Tracker import Tracker
from MessagesAndHandshakes import Handshake
from Metainfo import Metainfo
from FileReadWrite import FileReadWrite
from RequestManager import Requester
class  Torrent(object):
    'An object to handle all Torrent Activity'
    def __init__(self):
        self.file_addr         = sys.argv[1]
        self.metainfo          = Metainfo(self.file_addr)
        self.tracker           = Tracker(self, self.metainfo)
        self.handshake         = Handshake(self.metainfo, self.tracker)
        self.file_handler      = FileReadWrite(self.metainfo)
        self.requester         = Requester(self.metainfo, self.file_handler)
        self.peer_list         = list()
        self.buildPeerList()

    def buildPeerList(self):
        'Builds List of Peers from Tracker Data'
        temp_data = self.tracker.peers
        offset = 0
        peer = dict()
        while offset != len(temp_data):
            packed_peer, packed_port = struct.unpack_from("!iH", temp_data, offset)
            offset += 6
            peer['ip'] = socket.inet_ntoa(struct.pack("!i", packed_peer))
            peer['port'] = packed_port
            self.peer_list.append(peer)
