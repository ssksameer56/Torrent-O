#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import easygui

#Handle the Torrent Client for the user
import sys
from twisted.internet import reactor
import CoreTCP
import FileReadWrite
import MessagesAndHandshakes
import Metainfo
import RequestManager
import Tracker
from Torrent import Torrent

class TorrentGUI(object):

	'Quit the main program'
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		self.client.torrent.torrentQuit()		
		return False	
		
	'Function to make individual files button'
	def make_button(self, path):
		box = gtk.VBox(True, 0)
		box1 = gtk.VBox(False, 0)
		title_button = gtk.Button()
		label = gtk.Label(path)
		box1.pack_start(label, False, False, 3)
		label.show()
		title_button.add(box1)
		box1.show()
		
		separator = gtk.HSeparator()
		box1.pack_start(separator, False, True, 5)
		separator.show()    		
			
		'Adding the progressbar'	
		progressbar = gtk.ProgressBar(adjustment = None)
		progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
		progressbar.set_fraction(0.1)
		box1.add(progressbar)
		progressbar.show()

		separator = gtk.HSeparator()
		box1.pack_start(separator, False, True, 5)
		separator.show()  

		label = gtk.Label("File download in progress...")
		box1.pack_start(label, False, False, 3)
		label.show()
		
		box1.show()		
		box.pack_start(title_button, True, True, 0)
		title_button.show()
		box.show()
		return box

	'Makes a button of selected torrent file'
	def make_title_bar(self, path):
		self.client.initTorrent(path, reactor)
		self.title_button = self.make_button(self.client.torrent.metainfo.info['name'])
		self.outer_box.pack_start(self.title_button, False, False, 0)
		self.outer_box.pack_start(self.title_button, False, False, 0)
		self.title_button.show()
		self.outer_box.show()

	'Display a window for choosing a file and return the self.path of file chosen'
	def openfile(self, widget, data = None):
		self.path = easygui.fileopenbox()
		self.make_title_bar(self.path)
		
	def __init__(self, client):
	        'Create a window'
		self.client = client
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
     		self.title_button = gtk.HBox(True, 0)
     		
	     	'Adding a title to window'
		self.window.set_title("SSSS Torrent Client")
     	
     		'Set size of window'
		self.window.set_usize(600, 400)
     	
     		'Create self.outer_box, a  vertical box and add it to window. self.outer_box is main box of window to which widgets will be added'
		self.outer_box = gtk.VBox(False, 0)
		self.window.add(self.outer_box)
     	
     		'Adding horizontal separator to self.outer_box'
		separator = gtk.HSeparator()
		self.outer_box.pack_start(separator, False, True, 5)     
       
       		'Creating and adding "Open" button'
		box = gtk.HBox(True, 0)
		box2 = gtk.HBox(False, 0)
		open_button = gtk.Button()
		image = gtk.Image()
		image.set_from_file("Icons/open.png")
		label = gtk.Label("Open")
		box2.pack_start(image, False, False, 3)
		box2.pack_start(label, False, False, 3)
		open_button.add(box2)
		box.pack_start(open_button, True, True, 0)
		open_button.show()
		image.show()      	
 
		'Creating and adding "Play" button'
		box2 = gtk.HBox(False, 0)
		play_button = gtk.Button()
		image = gtk.Image()
		image.set_from_file("Icons/play.png")
		label = gtk.Label("Play")
		box2.pack_start(image, False, False, 3)
		box2.pack_start(label, False, False, 3)
		play_button.add(box2)
		box.pack_start(play_button, True, True, 0)
		play_button.show()
		image.show()        
        
        	'Creating and adding "Pause" button'
		box2 = gtk.HBox(False, 0)
		pause_button = gtk.Button()
		image = gtk.Image()
		image.set_from_file("Icons/pause.png")
		label = gtk.Label("Pause")
		box2.pack_start(image, False, False, 3)
		box2.pack_start(label, False, False, 3)
		pause_button.add(box2)
		box.pack_start(pause_button, True, True, 0)
		pause_button.show()
		image.show()         
 
 		'Adding above buttons to self.outer_box'
		self.outer_box.pack_start(box, False, False, 0)
        
        	'Adding two horizontal separators to self.outer_box'    
		separator = gtk.HSeparator()
		self.outer_box.pack_start(separator, False, True, 5)
		separator.show()     	
       
		separator = gtk.HSeparator()
		self.outer_box.pack_start(separator, False, True, 5)
		separator.show() 
            
        	'Connecting "open_button" to "openfile" function'
		open_button.connect("clicked",self.openfile, None)
		self.window.show_all()
