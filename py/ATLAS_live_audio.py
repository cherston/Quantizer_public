#!/usr/bin/python
#
#  Simple script to test XMLRPC image producing in Atlantis locally/in a debugger
#
#  - Start Atlantis with: 
#      java -Djava.awt.headless=true -jar atlantis.jar -I 7000
#  - In a different tab run this script:   python atlantis-xmlrpc-test.py
#  - Make sure the event file below exists
#
port  = 9001
#PATH_TO_DATA = "/Users/jcherston/Dropbox/Sonification_dist/1A"

#Below are paths to the unprocessed/processed data folders on the machine we are using to launch the platform
#PATH_TO_UNPROCESSED_DATA = "/Users/TRIUMF-ATLAS-DISPLAY/Documents/ATLAS_sonification_2015_ewan/file_transfer_scripts/downloading/downloaded_xml_files/latest"
#PATH_TO_PROCESSED_DATA = "/Users/TRIUMF-ATLAS-DISPLAY/Documents/ATLAS_sonification_2015_ewan/file_transfer_scripts/downloading/downloaded_xml_files/old"
PATH_TO_UNPROCESSED_DATA = "../data/unprocessed"
PATH_TO_PROCESSED_DATA = "../data/processed"

 

from xmlrpclib import ServerProxy
from xmlrpclib import Binary
import time
from Queue import Queue
from threading import Thread
from OSC_engine import OSC_engine
import os.path
import sys
import argparse
import os

next_event_id = 0
send_all = False
NUM_IDS = 2
COUNT = 0

def audio_engine(a,q,spatialize):
	global COUNT
	while (not q.full()):
  		try: 
			global next_event_id
			event=q.get()
			event_id = next_event_id
			next_event_id = (next_event_id + 1) % NUM_IDS  
			print "Processing event number: " + str(COUNT)
			COUNT+=1
			 
			print "Processing Event: ", event
			print "maxbeats: " + str(maxbeats)
			print "geometry: " + str(geometry)
			print "spatialize: " + str(spatialize)
			a.set_data(event,event_id,maxbeats,geometry,seconds,unif,poly) 
			if spatialize: 
				a.run_spatialize()
			else: 	
				a.run() 
			q.task_done()
	  	except: 
			print "NOT STREAMING EVENT" 
			print(sys.exc_info())

def audio_overlap(a,event,spatialize):
		try:
			global next_event_id
			event_id = next_event_id
			next_event_id = (next_event_id + 1) % NUM_IDS

			print "Processing Event: ", event
			print "maxbeats: " + str(maxbeats)
			print "geometry: " + str(geometry)
			print "spatialize: " + str(spatialize)
			a.set_data(event,event_id,maxbeats,geometry,seconds,unif,poly) 
			if spatialize: 
				a.run_spatialize()
			else: 	
				a.run() 
		except: 
			print(sys.exc_info()[0])


def generate_image(event): 
	png   = event.replace('.xml', '.png')
	thumb = event.replace('.xml', '.thumb.png')
	png2 = 'latest_event.png'
	server = ServerProxy('http://localhost:%d' % port)
	#server = ServerProxy('https://atlas-live.cern.ch/event_files/Main/')

	#if not server.atlantis.event.xmlrpc.AServerXMLRPCEventSource.isReady():
	#    print 'Server is not ready, try again later'
	#else:
	#    print "Requesting image and thumbnail for '%s'" % event

	images = server.atlantis.event.xmlrpc.AServerXMLRPCEventSource.generateDefaultImages(Binary(data), event, 1024, 0.1)

	open(png2, 'w').write(images[0].data)
	open(png, 'w').write(images[0].data)
	open(thumb, 'w').write(images[1].data)


def load_event(a,wait,overlap,spatialize):
	"""
	####temporary use of masterclass data
	for event in os.listdir(PATH_TO_DATA): 
		if (not event.endswith (".DS_Store")):
			q.put('1A/' + event)
			time.sleep(8)
	"""
	#CODE BELOW IS THE CORRECT CODE
	
	flag = True 
	if wait: 
		print "You are running in a test mode that allowed you to put lots of files in the unprocessed directory" 
		
	while 1: 
		new = os.listdir(PATH_TO_UNPROCESSED_DATA)
		if flag:
			print "MAINTHREAD: waiting for next event..."
			flag = False
			 
		if new:
			#sort the list to make sure that we're removing the newest files 
			#if running in normal mode, ensure that files don't pile up beyond 2
			if not wait:
				if len(new) > 2:
					for i in range(2,len(new)-1):
						try:
							print "trying to remove" + str(PATH_TO_UNPROCESSED_DATA + "/" + new[i])
							os.remove(PATH_TO_UNPROCESSED_DATA + "/" + new[i])
							print "removed"
						except OSError:
							pass
				new = os.listdir(PATH_TO_UNPROCESSED_DATA)
 
		
			time.sleep(1) 
			 
			new_path = PATH_TO_PROCESSED_DATA + "/" + new[0]
			
			print PATH_TO_UNPROCESSED_DATA
			#print os.path.exists(PATH_TO_UNPROCESSED_DATA)
	 
			
			
			os.rename(PATH_TO_UNPROCESSED_DATA + "/" + new[0], new_path)
			if not overlap: 
				q.put(new_path)
				print "MAINTHREAD: next event added to queue"
			else: 
				Thread(target=audio_overlap, args=(a,new_path,spatialize,)).start()
				print "MAINTHREAD: processed next event" 
			
			flag = True 
	
if __name__ == "__main__":
	
	parser=argparse.ArgumentParser()
	parser.add_argument("--geo", default='Eta', help="optional: select scanning geometry: 'Eta','Phi','absPhi' currently supported")
	parser.add_argument("--maxbeats", default = '40',help = "optional: set a max number of beats per data stream to be read in. By default will select highest energy values")
	parser.add_argument("--test", action='store_true', help="optional: only parse a single event")
	parser.add_argument("-c", action='store_true')
	parser.add_argument("--uniform", action='store_true', help="binary to dictate whether audio has a beat or is purely geometric")
	parser.add_argument("--seconds",default='30',help = "optional: number of seconds of audio per event")
	parser.add_argument("--spb", help = "Seconds per beat. NOTE: OVERRIDES SECONDS")
	parser.add_argument("--spatialize", default=False,help="binary to dictate whether detector layers should be streamed one at a time")
	parser.add_argument("--gui",default=False,help="binary to toggle GUI on and off for commandline selections")
	parser.add_argument("--layertimeratio",default=[1,1,1],help="time ratio for each of the 3 detector segments: tracks (inner detector), calorimeter, Muon Spectrometer. Only applicable with spatialize mode enabled")
	parser.add_argument("--overlap",default=False,help="Toggles whether events are queued or whether they are streamed as they arrive")
	parser.add_argument("--poly",default=False,help="determines whether multiple notes play at once")
	parser.add_argument("--send_all",action='store_true',help="0 delays between events, if you'd rather control timing in Pure Data or Max")
	parser.add_argument("--preamble",action='store_true',help="send event-level info 5 seconds before streaming the remaining data") 
	args = parser.parse_args()
 
	geometry = args.geo
	seconds = float(args.seconds)
	layer_ratio = args.layertimeratio
	poly = args.poly
	
	if args.send_all: 
		send_all = True
	
	if args.uniform:  
		unif = True
	else:
		unif = False
		
	if args.spb: 
		maxbeats = int(seconds/float(args.spb))
	else: 
		maxbeats = int(args.maxbeats)

	if args.test: 
		#event ='1A/1A_41_190343_88636558_413.xml'
		t0 = time.time()
		#event = "../data/1A/1A_35_190343_42131192_187.xml"
		event = "../data/JiveXML_264034_7064956_2015_05_May_com900GeV_minBias_noData.xml"
		a = OSC_engine(layer_ratio,send_all)
		a.set_data(event,next_event_id, maxbeats,"Eta",seconds,unif,poly) 
		print "time: " + str(time.time() - t0)
		if args.spatialize: 
			a.run_spatialize()
		else: 
			a.run() 
	
	else:
		if not args.overlap: 
			q = Queue(maxsize=900)
			a = OSC_engine(layer_ratio,send_all)
			worker = Thread(target=audio_engine, args=(a,q,args.spatialize,))
			worker.start()
		
		load_event(a,args.c,args.overlap,args.spatialize)
	