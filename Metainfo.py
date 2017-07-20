#Handles the Parsing of Torrent File to Generate Dictionary of Metainfo
from pprint import pprint
import hashlib
import bencoder
class Metainfo(object):
	'A Class to handle all the functions and data related to torrent metainfo'
	def __init__(self, file_addr):
		'Initializes all the variables'
		self.announce		= ""
		self.announce_list	= ""
		self.create_date	= ""
		self.comment		= ""
		self.created_by		= ""
		self.info		= ""
		self.encoding		= ""
		self.piece_length	= ""
		self.info_hash		= ""
		self.no_of_pieces	= ""
		self.files		= []
		self.length		= 0
		self.createMetainfo(file_addr)
		self.generateInfohash()

	def createMetainfo(self, file_arg):
		'Bdecodes the torrent file to generate torrent data'
		file_pointer = open(file_arg, "rb")
		file_data = file_pointer.read()
		try:
			temp_data = bencoder.decode(file_data)
		except bencode.BTFailure:
			raise ValueError("Invalid Torrent file")
		if 'announce' not in temp_data or 'info' not in temp_data:
			raise ValueError("Invalid Torrent file")
		self.announce		= temp_data['announce']
		self.info		= temp_data['info']

		if ('piece length' not in self.info
			or 'pieces' not in self.info
			or 'name' not in self.info):
			raise ValueError("Invalid BitTorrent metainfo file format")
		self.piece_length	= self.info['piece length']
		try:
			if 'length' in self.info:
				# Single file mode
				self.directory = ''
				self.files = [([self.info['name']], self.info['length'])]
				self.length = self.info['length']
			else:
				# Multi file mode
				self.directory = self.info['name']
				for d in temp_data['info']['files']:
					self.files.append((d['path'], d['length']))
					self.length += d['length']
		except:
			raise ValueError("Invalid BitTorrent metainfo file format")

		self.announce_list	= temp_data.get('announce-list', None)
		self.create_date	= temp_data.get('creation date', None)
		self.comment		= temp_data.get('comment', "")
		self.created_by		= temp_data.get('created by', "")
		self.encoding 		= temp_data.get('encoding', "")
		del temp_data, file_data
		file_pointer.close()

	def generateInfohash(self):
		'Bencodes the info dictionary and generates an SHA1 Hash'
		temp_obj = hashlib.sha1()
		temp_obj.update(bencoder.encode(self.info))
		self.info_hash = temp_obj.digest()
		del temp_obj

"""if __name__ == "__main__":
	abc = Metainfo("abc.torrent")
	pprint(abc.info)"""
