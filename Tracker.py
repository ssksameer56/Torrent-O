#Generates, handles and parses HTTP Trackers
import struct #Only for __main__
import socket #Only for __main__
import hashlib
import requests
import bencoder
import time
from Metainfo import Metainfo
from twisted.web.client import getPage
import random
import string

PEER_ID_START = '-KB1000-'
LOCAL_PORT = 6114

class Tracker(object):
    'A Class to handle all the functions and data related to trackers'
    def __init__(self, torrent, metainfo):
        'Initializes all variables'
        self.tracker_url= ""
	self.peer_id = "-HS0001-"+str(int(time.time())).zfill(12)
        #self.peer_id    = "-TR2110-000000000000"
        #TR2110 is the Peer Id for Transmission 2.1.10
        self.port               = LOCAL_PORT
        self.uploaded           = 0
        self.downloaded         = 0
        self.left               = 0
        self.event              = 'started'
        self.para_dict          = ""
        self.interval           = ""
        self.min_interval       = ""
        self.tracker_id         = ""
        self.complete           = "" #Seeders
        self.incomplete         = "" #Leechers
        self.peers              = ""
        self.tracker_response   = ""
        #self.findTorrentStatus(torrent)
        self.generateHTTPRequest(metainfo)
        self.httpRequest()
        #self.parseTrackerResponse()

    def findTorrentStatus(self, torrent):
        'Finds the status of torrent file'
        self.uploaded  = torrent.uploaded
        self.downloaded= torrent.downloaded
        self.left      = torrent.left
        self.peer_id   = torrent.peer_id

    def generateHTTPRequest(self, metainfo):
        'Creates a dictionary to pass to the Requests function'
	self.tracker_url	= metainfo.announce
	self.tracker_list	= metainfo.announce_list
	self.length		= metainfo.length
	#self.left = sum([pair[1] for pair in metainfo.files])
	N = 20 - len(PEER_ID_START)
	end = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(N))
	peer_id = PEER_ID_START + end
	self.para_dict = {}
	self.para_dict['info_hash']	= metainfo.info_hash
	self.para_dict['peer_id'] 	= self.peer_id
	self.para_dict['port']		= self.port
	self.para_dict['uploaded']	= self.uploaded
	self.para_dict['downloaded']	= self.downloaded
	self.para_dict['left']		= self.left
	self.para_dict['compact']	= 1
	self.para_dict['event']		= self.event

    def httpRequest(self):
        'Issues a GET request to the respective tracker'
	url     = self.tracker_url
	params  = self.para_dict
	self.tracker_response = requests.get(url, params = params)
	print self.tracker_response.text

    def parseTrackerResponse(self):
        'Parses the HTTP response from trackers'
        tracker_data = bencoder.decode(self.tracker_response.content)
        self.interval       = tracker_data['interval']
        self.min_interval   = tracker_data['min interval']
        self.peers          = tracker_data['peers'] #Peers are binary or dictionary model
