import math
import hashlib
import struct
import Tracker
import Metainfo

class FileReadWrite(object):
    'Class to Handle All File Read Write Operations'
    def __init__(self, metainfo):
        'Initializes all the variables needed'
        self.file_pointer   = None
        self.total_pieces   = math.ceil(len(metainfo.info['pieces'])/20) #Pieces are 20byte hashes
        self.total_length   = metainfo.info['length']
        self.piece_index    = 0
        self.block_index    = 0
        self.offset         = 0
        self.piece_hash     = list() #Store all the hashes of pieces
        self.piece_size     = metainfo.info['piece length']
        self.block_size     = 16384 #Standard 16 KB Blocks
        self.data_buffer    = ''
        self.no_of_blocks   = math.ceil(self.piece_size/self.block_size)
        self.completed      = False
        self.pieces_completed = list()
        self.createInfoDict(metainfo)
        self.openFile(metainfo)
	print self.__dict__

    def createInfoDict(self, metainfo):
        'Create a list of hashes to compare recieved data'
        offset = 0
        while offset != len(metainfo.info['pieces']):
            self.piece_hash.append(metainfo.info['pieces'][offset:(offset+20)])
            offset += 20

    def openFile(self, metainfo):
        'Create/Open File to Write'
        self.file_pointer = open(metainfo.info['name'], "wb+")
        while True:
            self.data_buffer = self.file_pointer.read(self.piece_size)
            if len(self.data_buffer) < self.piece_size:
		break
            hash_obj = hashlib.sha1()
            hash_obj.update(self.data_buffer)
            temp_piece = hash_obj.digest()
            if temp_piece == self.piece_hash[self.piece_index]:
                self.piece_index += 1
    def writeToBuffer(self, piece_index, block_index, data, requester):
        'Creates a buffer for a specific piece'
        if piece_index == self.piece_index:
            self.data_buffer[block_index:block_index + self.block_size] = data
            block_index += 1
        if len(self.data_buffer) == self.piece_length:
            self.writeToFile(requester)

    def writeToFile(self, requester):
        'Writes to a file when a piece is downloaded'
        hash_obj = hashlib.sha1()
        hash_obj.update(self.data_buffer)
        temp_piece = hash_obj.digest()
        if temp_piece == self.piece_hash[self.piece_index]:
            offset = self.piece_index * self.piece_size
            self.file_pointer.seek(offset, 0)
            self.file_pointer.write(self.data_buffer)
            self.block_index = 0
            self.pieces_completed.append(self.piece_index)
            self.piece_index += 1
            self.data_buffer = ''
            self.rem_pieces -= 1
	    requester.incrementPiece()

    def havePiece(self, piece_index, block_index):
        'Checks if the client has the piece downloaded'
        return bool(piece_index in self.pieces_completed)

    def readData(self, piece_index, block_index):
        'Reads Data to send to remote peer'
        data = ''
        current_offset = self.file_pointer.tell() # Remember where pointer was
        self.file_pointer.seek(0, piece_index*self.piece_size + block_index*self.block_size)
        data = self.file_pointer.read(self.block_size)
        self.file_pointer.seek(0, current_offset)
        return data

    def torrentQuit(self):
        'Completes writing file before quiting'
        self.file_pointer.write(self.data_buffer)
        self.file_pointer.close()
