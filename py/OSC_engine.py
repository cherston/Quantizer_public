#! /usr/bin/python
import OSC
import time
#from pyig.tests.EERecHits import EERec_Array
from threading import Thread 
import numpy as np
import XMLReader as reader 
import operator 
from analysis import Analysis
from Particles import Event
#from views import socketio 
import os
import time
import random


#event='mc12_160155_10959.xml' 
class OSC_engine:
	def __init__(self,layer_ratio = 111,send_all = False, frontload = False): 
		self.threads=[]
		# Init OSC
		self.client = OSC.OSCClient()
		self.client.connect(('127.0.0.1', 5002)) # first argument is the IP of the host, second argument is the port to use
		self.data = None
		self.track_time = float(layer_ratio[0])
		self.calo_time = float(layer_ratio[1])
		self.rpc_time = float(layer_ratio[2])
		#self.track_time = random.uniform(1,2)
		#self.calo_time = random.uniform(1,2)
		#self.rpc_time = random.uniform(1,2)
		self.t0 = time.time() 
		self.sendall = send_all
		self.frontload = frontload
		
	def set_data(self,ev,ev_id,beats,geo,seconds,unif,poly): 
		event = Event(ev)
		self.event_id = ev_id
		#print "Muons: " +str(event.muons)
		self.anal = Analysis(event,beats,geo,seconds,unif,poly)
		self.data = self.anal.event
		self.unif = unif
		
	def pkg_msg(self, data, addr): 
		oscmsg = OSC.OSCMessage(address="/%d%s" % (self.event_id, addr))
		#oscmsg.setAddress(address)
		oscmsg.append(data)
		return oscmsg
	
	def pkg_str(self, data, address): 
		oscmsg = OSC.OSCMessage('s')
		oscmsg.setAddress(address)
		oscmsg.append(data)
		return oscmsg
			
	def osc_scan_send(self,data,addr,delay): #sends data at a rate determined by geometric coordinate. NOTE: if I switch to bundle/thread method, can get rid of eta as parameter
		oscmsg = OSC.OSCMessage(address="/%d%s" % (self.event_id, addr))
		for a in range(len(data)): 
			oscmsg.append(data[a])
			self.client.send(oscmsg)
			oscmsg.clearData()
			if not self.sendall: 
				time.sleep(delay[a])
		return True
	
	def osc_scan_sendall(self,datasets,addr,delay): #sends data as single message per physics object 
		oscmsg = OSC.OSCMessage(address="/%d%s" % (self.event_id, addr))
		count = len(datasets[0])
		time.sleep(delay[0])
		for a in range(count): 
			for dataset in datasets: 
				oscmsg.append(dataset[a])
			self.client.send(oscmsg) 
			oscmsg.clearData()
			if not self.sendall: 
				time.sleep(delay[a+1])
		return True
				
			
	
		#This is the final delay step between the last particle hit and the edge of the detector
		#time.sleep(delay[len(delay)-1]) 
	
	def osc_bnd_send(self,oscmsgs): 
		oscbnd = OSC.OSCBundle()
		for oscmsg in oscmsgs: 
			oscbnd.append(oscmsg) 
		self.client.send(oscbnd) 
		
	def new_scan_thread(self,data, address,delay):
		thread=Thread(target=self.osc_scan_send, args=(data,address,delay))
		self.threads.append(thread)
		thread.start()
	
	def new_scan_all_thread(self,datasets, address,delay):
		thread=Thread(target=self.osc_scan_sendall, args=(datasets,address,delay))
		self.threads.append(thread)
		thread.start()

	def preamble(self):
		#self.client.send(self.pkg_msg(str(self.data.etmiss.getE()),'/EventInfo/etmiss'))
		#self.client.send(self.pkg_msg(self.data.Tracks.getEffectiveSum(),'/EventInfo/effectivesum'))
	
		msg1 = 0
		msg2 = 0
		
		#test_bundles
		if self.data.etmiss:
			msg1 = self.pkg_msg(self.data.etmiss.E, '/EventInfo/etmiss')
		print "effective sum: " + str(self.data.Tracks.getEffectiveSum())
		if self.data.Tracks.getEffectiveSum(): 
			msg2 = self.pkg_msg(self.data.Tracks.getEffectiveSum(),'/EventInfo/effectivesum')
		
		msglast = self.pkg_msg(1.0, '/EventInfo/start')
		if msg1 and msg2: 
			self.osc_bnd_send([msg1,msg2])
		self.client.send(msglast)
		if self.frontload: 
			print "waiting 5 seconds"
			time.sleep(5)

		 
	def run(self): 
		                                                                                                                                                                                                                                                                                                  
			
 		print "running non-spatialize"
 		
 		if self.unif: 
			self.anal.wait_for_beat(self.t0) 
		# opted to front-load sending event info 
		print "starting time: " + str(time.time())
		
		self.preamble()
		
		# sending remaining data multithreaded
		
		if self.data.RPC.size(): 
			#print "RPC size: " + str(len(self.data.RPC.getEta()))
			#print "RPC delay size: " + str(len(self.data.RPC.delays))
			RPC_delay=self.data.RPC.delays
			self.new_scan_all_thread([self.data.RPC.getEta(),self.data.RPC.getPhi(),self.data.RPC.getTheta()], '/RPC',RPC_delay)
			 
		if self.data.Tracks.size(): 
			Track_delay = self.data.Tracks.delays
			#print "Track size: " + str(len(self.data.Tracks.getEta()))
			#print "Track delay size: " + str(len(self.data.Tracks.delays))
			self.new_scan_all_thread([self.data.Tracks.getEta(),self.data.Tracks.getPhi(),self.data.Tracks.getE(),self.data.Tracks.getTheta(),self.data.Tracks.getPt()], '/Tracks',Track_delay)


			#print "track E: " + str(self.data.Tracks.getE())
		if self.data.LArHits.size(): 
			LAr_delay=self.data.LArHits.delays
			self.new_scan_all_thread([self.data.LArHits.getEta(),self.data.LArHits.getPhi(),self.data.LArHits.getE(),self.data.LArHits.getTheta()], '/LArHits',LAr_delay)
			
		if self.data.HECHits.size():
			HEC_delay=self.data.HECHits.delays
			self.new_scan_all_thread([self.data.HECHits.getEta(),self.data.HECHits.getPhi(),self.data.HECHits.getE(),self.data.HECHits.getTheta()], '/HECHits',HEC_delay)

		# THREADS #
		for thread in self.threads: 
			thread.join()
		
		self.t0 = time.time()
		
	def run_spatialize(self): 
		print "running spatialize"
		
		if self.unif: 
			self.anal.wait_for_beat(self.t0)

		self.preamble()
		
		if self.data.Tracks.size(): 
			Track_delay = self.data.Tracks.delays
 
 			#single_track_delay = self.data.Tracks.single_track_delay
			
			#Final adjustment of timing based on user preferences 
			Track_delay = [i/self.track_time for i in Track_delay]
			
			#ToDo: 
			#Recalculate delays based on how long each detector segment should be processed for
			
			self.new_scan_all_thread([self.data.Tracks.getEta(),self.data.Tracks.getPhi(),self.data.Tracks.getE(),self.data.Tracks.getTheta(),self.data.Tracks.getPt()], '/Tracks',Track_delay)

			#Code below is to stream polyline associated with track. Removed for now in favor of 
			#only streaming Pt
			
 			for thread in self.threads: 
				thread.join()
			
		
		self.threads = []
 
		if self.data.LArHits.size(): 
			LAr_delay=self.data.LArHits.delays
			
			#Final adjustment of timing based on user preferences 
			LAr_delay = [i/self.calo_time for i in LAr_delay]
			self.new_scan_all_thread([self.data.LArHits.getEta(),self.data.LArHits.getPhi(),self.data.LArHits.getE(),self.data.LArHits.getTheta()], '/LArHits',LAr_delay)

		if self.data.HECHits.size():
			HEC_delay=self.data.HECHits.delays
			
			#Final adjustment of timing based on user preferences 
			HEC_delay = [i/self.calo_time for i in HEC_delay]
			self.new_scan_all_thread([self.data.HECHits.getEta(),self.data.HECHits.getPhi(),self.data.HECHits.getE(),self.data.HECHits.getTheta()], '/HECHits',HEC_delay)

			for thread in self.threads: 
				thread.join()
				
		self.threads = []	
			
		if self.data.RPC.size(): 
			print self.data.RPC.delays
			RPC_delay=self.data.RPC.delays
			
			#Final adjustment of timing based on user preferences
			RPC_delay = [i/self.rpc_time for i in RPC_delay]
			self.new_scan_all_thread([self.data.RPC.getEta(),self.data.RPC.getPhi(),self.data.RPC.getTheta()], '/RPC',RPC_delay)

		for thread in self.threads: 
			thread.join()
	  
		self.t0 = time.time()
		print "final time: " + str(self.t0)
		
		"""	
		################## For web streaming via socketio

		def sendtoweb(self, data, delay):
			for a in range(len(data)): 
				#time.sleep(self.anal.SECONDS/self.anal.TOTRANGE*delay[a])
				time.sleep(3) 
				socketio.emit('my response', {'data': 'Muon generated event', 'value': data[a]},
				namespace='/music') 
		
		def socket_stream(self, data, delay):
			thread=Thread(target=sendtoweb, args=(data,delay))
			self.webthreads.append(thread) 
			thread.start() 

		##################	
		"""
		return True

 
