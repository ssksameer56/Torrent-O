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
		self.info			= ""
		self.encoding		= ""
		self.piece_length	= ""
		self.info_hash		= ""
		self.no_of_pieces	= ""
		self.createMetainfo(file_addr)
		self.generateInfohash()
		print self.__dict__

	def createMetainfo(self, file_arg):
		'Bdecodes the torrent file to generate torrent data'
		file_pointer = open(file_arg, "rb")
		file_data = file_pointer.read()
		temp_data = bencoder.decode(file_data)
		self.announce		= temp_data['announce']
		self.announce_list	= temp_data['announce-list']
		self.create_date	= temp_data['creation date']
		self.comment		= temp_data['comment']
		self.created_by		= temp_data['created by']
		self.info		= temp_data['info']
		self.piece_length	= self.info['piece length']
		#self.encoding 		= temp_data['encoding']
		del temp_data, file_data
		file_pointer.close()

	def generateInfohash(self):
		'Bencodes the info dictionary and generates an SHA1 Hash'
		temp_obj = hashlib.sha1()
		temp_obj.update(bencoder.encode(self.info))
		self.info_hash = temp_obj.digest()
		del temp_obj

if __name__ == "__main__":
	abc = Metainfo("abc.torrent")
	pprint(abc.info)
