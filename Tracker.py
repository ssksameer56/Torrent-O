#Generates, handles and parses HTTP Trackers
import struct #Only for __main__
import socket #Only for __main__
import hashlib
import requests
import bencoder
from Metainfo import Metainfo

class Tracker(object):
    'A Class to handle all the functions and data related to trackers'
    def __init__(self, torrent, metainfo):
        'Initializes all variables'
        self.tracker_url= ""
        self.peer_id    = "-TR2110-000000000000"
        #TR2110 is the Peer Id for Transmission 2.1.10
        self.port               = 6114
        self.uploaded           = 0
        self.downloaded         = 0
        self.left               = 100
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
        self.parseTrackerResponse()

    def findTorrentStatus(self, torrent):
        'Finds the status of torrent file'
        self.uploaded  = torrent.uploaded
        self.downloaded= torrent.downloaded
        self.left      = torrent.left
        self.peer_id   = torrent.peer_id

    def generateHTTPRequest(self, metainfo):
        'Creates a dictionary to pass to the Requests function'
        self.tracker_url    = metainfo.announce
        self.tracker_list   = metainfo.announce_list
        self.para_dict      = {'info_hash':metainfo.info_hash, 'peer_id':self.peer_id,\
                                'port':self.port, 'uploaded':self.uploaded,\
                                'downloaded':self.downloaded, 'left':self.left,\
                                'event':self.event}

    def httpRequest(self):
        'Issues a GET request to the respective tracker'
        url     = self.tracker_url
        params  = self.para_dict
        self.tracker_response = requests.get(url, params = params)

    def parseTrackerResponse(self):
        'Parses the HTTP response from trackers'
        tracker_data = bencoder.decode(self.tracker_response.content)
        self.interval       = tracker_data['interval']
        self.min_interval   = tracker_data['min interval']
        self.peers          = tracker_data['peers'] #Peers are binary or dictionary model
