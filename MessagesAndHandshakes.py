#Classes to Handle Messages and Handshakes
import struct
import Tracker
import Metainfo

class Handshake(object):
    'Class to manage all handshake data'

    def __init__(self, metainfo, tracker):
        'Initializes variables for a handshake'
        self.str_len    = ''
        self.str        = ''
        self.reserved   = ''
        self.info_hash  = ''
        self.peer_id    = ''
        self.generateHandshake(metainfo, tracker)

    def generateHandshake(self, metainfo, tracker):
        'Returns a payload containing handshake'
        self.str_len    = chr(19)
        self.str        = "bittorrent protocol"
        self.reserved   = "\x00\x00\x00\x00\x00\x00\x00\x00"
        self.info_hash  = metainfo.info_hash
        self.peer_id    = tracker.peer_id
        return self.str_len + self.str + self.reserved + self.info_hash+ self.peer_id

class Message(object):
    'Generic parent message class'
    protocol_args = [] #For generic 4 byte data
    protocol_extended = None # For special data like bitfield, peices

    def __init__(self,**kwargs):
        'Initializes according to data'
        if 'response' in kwargs:
            self.setupFromResponse(kwargs['response'])
        elif set(self.protocol_args + ([self.protocol_extended] if self.protocol_extended else []))\
                    == set(kwargs.keys()):
            self.setupFromArgs(kwargs)

    def setupFromResponse(self, response):
        'Setup the message object if it iis reieved from remote peer'
        payload		= response
        self.length 	= struct.unpackfrom("!i", payload)
        if self.length != 0 :
            self.msg_id = struct.unpack_from("!B", payload, 4) # 5th byte is the  msg_id
        else:
            self.msg_id = ''
        offset = 5 #Actual Data begins from 5th  byte
        for arg in self.protocol_args:
            setattr(self, arg, struct.unpackfrom("!i", payload, offset))
            offset += 4
        if self.protocol_extended :
            setattr(self, self.protocol_extended, payload[offset:])

def setupFromArgs(self, **kwargs):
    'Setup the message object for sending to remote peer'
    for arg in self.protocol_args:
        data = struct.pack("!i", kwargs[arg])
        setattr(self, arg, data)
    if self.protocol_extended :
        setattr(self, self.protocol_extended, kwargs[self.protocol_extended])
    length = 0
    if self.msg_id != '' :
        length = sum(len(x) for x in kwargs.values()) + 1
    self.msg_length = struct.pack("!i", length)

    def __str__(self):
        'Modifies the defualt str function to return payload'
        s = ''
        s += self.msg_length
        if self.msg_id != '':
            s += chr(self.msg_id)
            for arg in self.protocol_args:
                s += str(getattr(self, arg))
            if self.protocol_extended:
                s += getattr(self, self.protocol_extended)
        return s

class Keep_Alive(Message):
    msg_id = ''

class Choke(Message):
    msg_id = 0

class Unchoke(Message):
    msg_id = 1

class Interested(Message):
    msg_id = 2

class Not_Interested(Message):
    msg_id = 3

class Have(Message):
    protocol_args = ['index']
    msg_id = 4

class Bitfield(Message):
    protocol_extended = 'bitfield'
    msg_id = 5

class Request(Message):
    protocol_args = ['index','begin','length']
    msg_id = 6

class Piece(Message):
    protocol_args = ['index','begin']
    protocol_extended = 'piece'
    msg_id = 7

class Cancel(Message):
    protocol_args = ['index','begin','length']
    msg_id = 8

class Port(Message):
    protocol_extended = 'listen_port'
    msg_id = 9
