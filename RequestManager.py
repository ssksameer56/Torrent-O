#Class to Generate Requests for Peers
import math
import Queue

class Requester(object):
    'Handles, Generates all the Requests for the Client'
    def __init__(self, torrent, metainfo):
	'Initializes all variables required'
        self.request_queue           = Queue.Queue()
        self.current_piece_index    = torrent.file_handler.piece_index
        self.current_block_index    = torrent.file_handler.block_index
        self.block_size             = torrent.file_handler.block_size
        self.piece_size             = torrent.file_handler.piece_size
        self.total_pieces           = torrent.file_handler.total_pieces
        self.no_of_blocks           = math.ceil(self.piece_size/self.block_size)
        self.total_requests         = ''
        self.generateRequestQueue()

    def generateRequestQueue(self):
        'Generates a new Request Queue'
        self.total_requests = 0
        for i in range(int(self.no_of_blocks)):
            self.request_queue.put([self.current_piece_index,i])
            self.total_requests += 1

    def generateNewRequest(self):
        'Generates a new request to pass to peer'
        ret_index = self.request_queue.get() # ret_index = [piece_index, block_index]
        return ret_index[0], ret_index[1]

    def incrementPiece(self):
        'Modifies the Queue to generate a new one'
        self.current_piece_index += 1
        while self.request_queue.empty() is False:
            self.request_queue.get()
        self.generateRequestQueue()

    def reEnqueueRequest(self, piece_index, block_index):
        'Reenqueues the request if it is not satisfied'
        self.request_queue.put([piece_index, block_index])
