#Class to Connect to Peers and Respond to Events using Twisted Reactor, clientFactory and TCP Client
import time
import socket
import struct
import os
from twisted.internet import reactor, protocol
import Tracker
import Metainfo
import MessagesAndHandshakes #Going to rename the module to something simpler
from bitarray import bitarray
from Torrent import Torrent

class PeerConnection(protocol.Protocol):
    'Class to handle a single TCP connection to a peer'
    def __init__(self, torrent):
        'Initialize all important data'
        self.torrent                    = torrent
        self.pending_requests           = 10
        self.client_interested          = True
        self.peer_interested            = False
        self.client_choked              = True
        #The client is always interested and looking for more peers
        self.peer_choked 		= False
        self.blocks_requested           = set()
        self.peer_has_pieces            = list()
        self.peer_bitfield              = bitarray(0*self.torrent.metainfo.no_of_pieces)
        self.peer_ip                    = ''
        self.peer_port                  = ''
        self.factory                    = ''

    def connectionMade(self):
        'Handle successful connection to remote peer'
        self.factory 			= self.transport.connector.factory
        self.peer_ip 			= self.transport.connector.host
        self.peer_port 			= self.transport.connector.port
        self.transport.write(self.torrent.handshake_message)

    def dataReceived(self, data):
        'Handles all incoming data'
        message = data
        if message[1:20] == "bittorrent protocol":
            self.parseHandshake(message)
        else:
            self.parseMessages(message)
        if self.canSendRequests() is True:
            self.sendNextRequest()

    def parseHandshake(self, message):
        'Verifies the Handshake and proceeds to show interest and send bitfield'
        flag = False
        if  message[0] == self.handshake_message.str_len and \
            message[1:20] == self.handshake_message.str and \
            message[20:28] == self.handshake_message.reserved and \
            message[28:48] == self.handshake_message.info_hash and \
            message[48:68] == self.handshake_message.peer_id :
            flag = True
        if flag is True:
            self.factory.peers_handshaken.add(self.peer_ip, self.peer_port)
	    self.peer_choked = False
            self.transport.write(str( MessagesAndHandshakes.Interested() ))
            self.transport.write(str( MessagesAndHandshakes.Bitfield(bitfield = self.bitfield) ))
	else:
	    self.transport.loseConnection()

    def parseMessages(self, data):
        'Parses message and redirects to appropriate function'
        message = None
        msg_type = struct.unpack_from("!i", data)
        if msg_type == 0 :
            message = MessagesAndHandshakes.Keep_Alive(response=data)
        else:
            message =   {
                        0: lambda: MessagesAndHandshakes.Choke(response=data),
			            1: lambda: MessagesAndHandshakes.Unchoke(response=data),
                        2: lambda: MessagesAndHandshakes.Interested(response=data),
                        3: lambda: MessagesAndHandshakes.Not_Interested(response=data),
                        4: lambda: MessagesAndHandshakes.Have(response=data),
                        6: lambda: MessagesAndHandshakes.Request(response=data),
                        7: lambda: MessagesAndHandshakes.Piece(response=data),
                        8: lambda: MessagesAndHandshakes.Cancel(response=data),
                        9: lambda: MessagesAndHandshakes.Port(response=data),
                        }[struct.unpack_from("!B", data, 4)]()
        self.processMessage(message)

    def processMessage(self, message):
        'Takes action according to the type of message'
        if isinstance(message, MessagesAndHandshakes.Keep_Alive):
            pass
        if isinstance(message, MessagesAndHandshakes.Choke):
            self.client_choked = True
        if isinstance(message, MessagesAndHandshakes.Unchoke):
            self.client_choked = False
        if isinstance(message, MessagesAndHandshakes.Interested):
            self.peer_interested = True
        if isinstance(message, MessagesAndHandshakes.Not_Interested):
            self.peer_interested = False
        if isinstance(message, MessagesAndHandshakes.Have):
            self.peer_has_pieces.append(message.index)
            self.peer_bitfield.insert(message.index+1, True) # Peer has the piece
            if self.peer_interested is False:
                self.peer_interested = True
        if isinstance(message, MessagesAndHandshakes.Bitfield):
            self.peer_bitfield = message.bitfield
            i = 0
            for i in range(len(self.peer_bitfield)):
                if self.peer_bitfield[i] is True:
                    self.peer_has_pieces.append(i)
        if isinstance(message, MessagesAndHandshakes.Request):
            self.handleRequest(message)
        if isinstance(message, MessagesAndHandshakes.Piece):
            self.handleData(message)
        if isinstance(message, MessagesAndHandshakes.Cancel):
            self.cancelRequests(message)

    def handleRequest(self, message):
        'Handles incoming piece requests from Peers'
        if self.peer_choked is False and self.client_interested is True:
            if self.torrent.file_handler.havePiece(message.index, message.begin):
                data = self.torrent.file_handler.readData(message.index, message.begin)
                msg_obj = MessagesAndHandshakes.Piece(index = message.index,\
                          begin = message.begin, piece = data)
                self.transport.write(str(msg_obj))
    def handleData(self, message):
        'Writes the recieved data to a buffer'
        data = message.piece
        self.torrent.file_handler.writeToBuffer(message.index, message.begin, data)

    def canSendRequests(self):
        'Checks if more requests to peer are possible'
        if self.pending_requests >= 10 :
            return False
        else:
            return True

    def sendNextRequest(self):
        'Sends next request to the peer'
        piece_index, block_index = self.torrent.requester.generateNewRequest()
        block_size = self.torrent.file_handler.block_size
        if piece_index in self.peer_has_pieces:
            msg_obj    = MessagesAndHandshakes.Request(index = piece_index,\
                                                    begin = block_index,\
                                                    length = block_size)
            self.transport.write(str(msg_obj))
            self.pending_requests += 1
            self.blocks_requested.add([piece_index, block_index])
	else:
	    self.transport.write(str(MessagesAndHandshakes.KeepAlive())
	    self.torrent.requester.reEnqueueRequest(piece_index, block_index])

class PeerConnectionFactory(protocol.ClientFactory):
    'Class to handle all TCP connections. Keeps track of all persistent information'
    def __init__(self, torrent):
        'Initializes variables for TCP Factory'
        self.torrent              = torrent
        self.peer_list            = torrent.peer_list
        self.peers_connected_to   = list()
        self.peers_handshaken     = list()

    def removePeer(self, peer_ip, peer_port):
        'Removes peer from active connections'
        self.peers_connected_to.remove((peer_ip, peer_port))

    def buildProtocol(self, addr):
        'Builds individial TCP Connections for each peer'
        peer = PeerConnection(self.torrent)
        self.peers_connected_to.append((addr.host, addr.port))
        return peer

    def clientConnectionLost(self, connector):
        'Handle connection loss to remote peer'
        self.removePeer(connector.host, connector.port)

    def clientConnectionFailed(self, connector):
        'Handle connection failure to remote peer'
        connector.connect() #Tries to reconnect
