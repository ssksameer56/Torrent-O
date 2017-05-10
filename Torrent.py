#Class to handle all aspects of torrent
import struct
import socket
from bitarray import bitarray
import sys
from Tracker import Tracker
from MessagesAndHandshakes import Handshake
from Metainfo import Metainfo
from FileReadWrite import FileReadWrite
from RequestManager import Requester
from twisted.internet import reactor
import CoreTCP
class  Torrent(object):
    'An object to handle all Torrent Activity'
    def __init__(self, addr, t_reactor):
        self.reactor           = t_reactor
        self.file_addr         = addr
        self.metainfo          = Metainfo(self.file_addr)
        self.tracker           = Tracker(self, self.metainfo)
        self.handshake_message = Handshake(self.metainfo, self.tracker)
        self.file_handler      = FileReadWrite(self.metainfo)
        self.requester         = Requester(self, self.metainfo)
	self.bitfield          = bitarray(0*self.metainfo.no_of_pieces)
        self.peer_list         = list()
        self.buildPeerList()
        self.protocol_factory  = CoreTCP.PeerConnectionFactory(self)
	print self.peer_list

    def buildPeerList(self):
        'Builds List of Peers from Tracker Data'
        temp_data = self.tracker.peers
        offset = 0
        while offset < len(temp_data):
            peer = {'ip' : '', 'port' : ''}
	    packed_peer, packed_port= struct.unpack_from("!iH", temp_data, offset = offset)
            offset += 6
	    peer['ip'] = socket.inet_ntoa(struct.pack("!i", packed_peer))
            peer['port'] = packed_port
            self.peer_list.append(peer)

    def torrentStart(self):
        'Starts the torrent downloading'
        for peer in self.peer_list:
            if not(peer in self.protocol_factory.peers_connected_to):
                self.reactor.connectTCP(peer['ip'], peer['port'], self.protocol_factory, timeout=30)
                self.protocol_factory.peers_connected_to.append(peer)
		print peer
	self.reactor.run()
	

    def torrentQuit(self):
        'Performs cleanup when torrent client is to be closed'
        self.file_handler.torrentQuit()
	self.reactor.stop

    def torrentComplete(self):
        'Called if torrent is complete'
        self.file_handler.torrentQuit()
        reactor.stop()
