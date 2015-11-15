import numpy as np
from Particles import ParticleCollection, Event
import operator
from Utils import find_nearest
import random
import csv
import time
from random import randint
import subprocess
 

# To use analysis class: first run analyze to apply data cuts. Then run SetGEO to calculate delays

ARTIF_TRACK_CUT = 1 #Track Pt cut

#should replace with a "None" of some sort to distinguish 0 from 'unpopulated' in sparse uniform map array
HACK = 1000
UPLOAD = True

class Analysis(object): 
	def __init__(self, ev, beats, geo, seconds,unif,poly):
		self.MAXBEATS = beats 
		self.SECONDS = seconds
		self.TOTRANGE = None
		self.MIN = None
		self.MAX = None 
		self.UNIFORM_DIST = unif
		self.POLY = poly
		print "seconds: " + str(self.SECONDS)
		self.event = ev
		self.analyze()
 		self.setGeo(geo)
		self.write_metadata()

	def analyze(self):
		#Apply eta basic cuts 
		"""##############################################################"""
		#eta cuts taken from: http://arxiv.org/pdf/1409.8639.pdf
		signal = lambda x: np.fabs(x.Eta) < 2.4
		print "number of HECHits (before cuts): " + str(self.event.HECHits.size())
		self.event.HECHits = ParticleCollection(filter(signal, self.event.HECHits))
		print "number of HECHits (after cuts): " + str(self.event.HECHits.size())
		
		print "number of LArHits (before cuts): " + str(self.event.LArHits.size())
		self.event.LArHits = ParticleCollection(filter(signal, self.event.LArHits))
		print "number of LArHits (after cuts): " + str(self.event.LArHits.size())
		
		"""##############################################################"""
	
		#Apply artificial artificial track Pt cut 
		
		if self.event.Tracks.size(): 
			signal = lambda x: abs(x.Pt) >= ARTIF_TRACK_CUT
			print "number of Tracks (before cuts): " + str(self.event.Tracks.size())
			self.event.Tracks = ParticleCollection(filter(signal, self.event.Tracks))
			print "resuting track momentums: " + str(self.event.Tracks.getPt())
			print "number of Tracks (after cuts): " + str(self.event.Tracks.size())
		
		#Apply artificial cut on RPC: Top n phi values (which will then presumably be streamed to audio in order of eta coordinate) 
		randomnum = randint(1,9)
		if self.event.RPC.size() > int(self.MAXBEATS/2): 
			num = randint(self.MAXBEATS/2,self.MAXBEATS)
			print "number of RPC (before cuts): " + str(self.event.RPC.size())
			self.event.RPC.particles = (sorted(self.event.RPC.particles,key = operator.attrgetter("Phi"), reverse = True))[:num]
			print "number of RPC (after cuts): " + str(self.event.RPC.size())
		else:
			print "number of RPC (no cuts): " + str(self.event.RPC.size())

	
		
		
		#Apply boundary cuts based on values set as boundaries in PD GUI. These are artificially chosen based on anticipated data ranges
		#5/29: THESE VALUES ARE ALL HARDCODED AND THE WHOLE IMPLEMENTATION SHOULD BE CLEANED UP FOR V2
		"""##############################################################"""
		
		if self.event.LArHits.size(): 
			print "number of LArHits (before energy cuts): " + str(self.event.LArHits.size())
			#print self.event.LArHits.getE()
			signal = lambda x: x.E > .05 and x.E < 0.1
			self.event.LArHits = ParticleCollection(filter(signal, self.event.LArHits))
			print "number of LArHits (after energy cuts): " + str(self.event.LArHits.size())
		
		if self.event.HECHits.size(): 
			print "number of HECHits (before energy cuts): " + str(self.event.HECHits.size())
			signal = lambda x: x.E > .61 and x.E < 1.2
			self.event.HECHits = ParticleCollection(filter(signal, self.event.HECHits)) 
			print "number of HECHits (after energy cuts): " + str(self.event.HECHits.size())
		
		if self.event.Tracks.size(): 
			for p in self.event.Tracks.particles: 
				if p.E < 5:
					p.E = 5 + random.uniform(0,2)
				if p.E > 40:
					p.E = 40 
					
		if self.event.RPC.size(): 
			for p in self.event.RPC.particles: 
				if p.Eta < -2.4:
					p.Eta = -2.4
				if p.Eta > 2.4:
					p.Eta = 2.4
		"""##############################################################"""		
		
		return self.event 

 
	def setGeo(self, geo):
		self.GEO = geo
		if self.GEO == 'Eta': 
			#Ewan: -6 to 6 for entire detector: we'll have higher data values 
			self.MIN = -2.4
			self.MAX = 2.4
			 
		if self.GEO == 'Phi': 
			self.MIN = -np.pi 
			self.MAX = np.pi 
			 
		if self.GEO == 'absPhi': 
			self.MIN = 0
			self.MAX = np.pi
			 
		if self.GEO == 'Theta': 
			self.MIN = .181
			self.MAX = 2.96  
			
		self.TOTRANGE = self.MAX-self.MIN 
			
		if self.POLY: 
			if self.event.Tracks.size(): 
				self.event.Tracks = self.calcPolyDelays(self.event.Tracks)
			
			if self.event.RPC.size(): 
				self.event.RPC = self.calcPolyDelays(self.event.RPC) 
				#self.event.LArHits = self.calcPolyDelays(self.event.LArHits)
				#self.event.HECHits = self.calcPolyDelays(self.event.HECHits)
			
			
			#keeps calo on beat
			LAr_intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
			self.event.LArHits.particles = self.dense_uniformcut(self.event.LArHits,LAr_intervals)
			
			#NOTE: May want to change HEC_intervals to better reflect geometry 
			HEC_intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
			self.event.HECHits.particles = self.dense_uniformcut(self.event.HECHits,HEC_intervals)
			
			self.event.LArHits = self.calcDelays(self.event.LArHits)
			self.event.HECHits = self.calcDelays(self.event.HECHits)	
		 
		else: 
 			if self.UNIFORM_DIST: 
				if self.event.RPC.size(): 
					self.event.RPC.particles, self.event.RPC.sparse_uniform_map = self.sparse_uniformcut(self.event.RPC)
				
				if self.event.Tracks.size(): 
					self.event.Tracks.particles, self.event.Tracks.sparse_uniform_map = self.sparse_uniformcut(self.event.Tracks)
			
				if self.event.LArHits.size(): 
					LAr_intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
					self.event.LArHits.particles = self.dense_uniformcut(self.event.LArHits,LAr_intervals)
			
				if self.event.HECHits.size(): 
					#NOTE: May want to change HEC_intervals to better reflect geometry 
					HEC_intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
					self.event.HECHits.particles = self.dense_uniformcut(self.event.HECHits,HEC_intervals)
				
				if self.event.Tracks.size(): 
					self.event.Tracks = self.calcDelays(self.event.Tracks)
				
				if self.event.RPC.size(): 
					self.event.RPC = self.calcDelays(self.event.RPC) 
				
				if self.event.LArHits.size(): 
					self.event.LArHits = self.calcDelays(self.event.LArHits)
				
				if self.event.HECHits.size(): 
					self.event.HECHits = self.calcDelays(self.event.HECHits)
		
			elif not self.UNIFORM_DIST:
				
				#Apply max beat cuts (if a max beat is specified). Takes N=MAXBEATS calo hits with highest energy
				#Note that the selected geometry is still respected (ie/top 30 hits will then be streamed according to e.g. eta values)
				#Also note that this cut does not apply if uniform distribution is specified (see uniformcut function below)
				"""##############################################################"""
				self.event.HECHits.particles = (sorted(self.event.HECHits.particles,key = operator.attrgetter("E"), reverse = True))[:self.MAXBEATS]
				print "number of HECHits (after beat cuts): " + str(self.event.HECHits.size())
		
				self.event.LArHits.particles = (sorted(self.event.LArHits.particles,key = operator.attrgetter("E"), reverse = True))[:self.MAXBEATS]
				print "number of LArHits (after beat cuts): " + str(self.event.LArHits.size())
				"""##############################################################"""
				
				self.event.Tracks = self.calcNonUniformDelays(self.event.Tracks)
				self.event.RPC = self.calcNonUniformDelays(self.event.RPC) 
				self.event.LArHits = self.calcNonUniformDelays(self.event.LArHits)
				self.event.HECHits = self.calcNonUniformDelays(self.event.HECHits)
			
		
		
 
			
 		
	 
	"""
	sparse_uniformcut is for sparser data streams, e.g. tracks. Every track will be assigned a beat
	
	dense_uniformcut is for larger data streams e.g. calorimeter hits. Every beat interval is populated
	with the particle closest to it. 
	

	"""
	

			
	def sparse_uniformcut(self, particle_col): 
		if particle_col.particles: 
			# first, sort the particles in the collection by eta coordinate
			particle_col.particles = sorted(particle_col.particles,key=operator.attrgetter(self.GEO))
			
			#create a record which specifies which beats the particles will play at
			record = np.array([HACK]*(self.MAXBEATS))
			
			#create even geometric intervals that each beach will correspond to
			intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
			
			#for each particle or physics object in the collection...
			for p_idx, p in enumerate(particle_col.particles): 
			
				#find the closest interval that the geometric coordinate of the particle corresponds to 
				index = find_nearest(intervals,getattr(p, self.GEO))
				while HACK in record:
					new_order = filter(lambda a: a!=HACK,record)
 					if record[index] == HACK: 
 						record[index] = p_idx
						break 
					#set the next indices to check if the previous was occupied 
					else:
 						available = np.where(record == HACK)[0]
						closest_available_index = available[find_nearest(available,index)]
			 
						record[closest_available_index] = p_idx
						break 
			
			#even though we intend to sort particles by eta, the above clustering could cause some particles to flip. 
			#therefore, we use the new order below 
			new_order = filter(lambda a: a!=HACK,record)
	
			particle_col.particles = [particle_col.particles[i] for i in new_order]
			
			return particle_col.particles, record

		
	def dense_uniformcut(self, particle_col,selected_intervals): 
		if particle_col.particles: 
			particle_col.particles = sorted(particle_col.particles,key=operator.attrgetter(self.GEO))
			particles = []
			intervals = selected_intervals
			#intervals = np.linspace(self.MIN,self.MAX,self.MAXBEATS)
			for i in intervals:
				method = getattr(particle_col, 'get' + self.GEO)() 
				if len(method) > 0: 
					index = find_nearest(method,i)
					particles.append(particle_col.particles[index])
					particle_col.particles = np.delete(particle_col.particles,index)
			return particles 
		
		
	def calcDelays(self, particle_col):
		#assume physics object lists are already sorted appropriated from the sparse/dense uniform cut functions
		#print type(particle_col.particles)
		if particle_col.particles: 
			#print "number of particles we're calculating delays for: " + str(len(particle_col.particles))
			size = len(particle_col.sparse_uniform_map)
			if size == 0: #ie/if dense uniform cut was applied rather than sparse uniform cut 
				a = np.empty(self.MAXBEATS)
				inc = float(self.SECONDS)/float(self.MAXBEATS)
 				a.fill(inc)
 				a = np.append(a,0)
 				a = np.insert(a,0,0)
 				print "length: " + str(len(a))
				delays = a
				
			else:
				delays = []
				delay = 0
				#print "map: " + str(len(particle_col.sparse_uniform_map))
				for i in range(0,len(particle_col.sparse_uniform_map)): 
					if particle_col.sparse_uniform_map[i] == HACK:
						delay += float(self.SECONDS)/float(self.MAXBEATS)
					else: 
						delays.append(delay)
						delay = float(self.SECONDS)/float(self.MAXBEATS)
				
				#change some delays to 0 
				#delays.append(delay)
			delays = np.append(delays,0)
 			delays = np.insert(delays,0,0)
 			print "length: " + str(len(delays))
			particle_col.delays = delays
	
		return particle_col
		
	def calcNonUniformDelays(self,particle_col): 
		if particle_col.particles: 
			#we still need to sort
			particle_col.particles = sorted(particle_col.particles,key=operator.attrgetter(self.GEO))
			method = getattr(particle_col, 'get' + self.GEO)() 
			a = np.concatenate([[self.MIN],(method),[self.MAX]])
			delays = np.absolute(np.ediff1d(a))
			delays = [i * self.SECONDS/self.TOTRANGE for i in delays]
			#delays = np.concatenate([(a),[0]])	
			particle_col.delays = delays
	
		return particle_col
		
	def calcPolyDelays(self, particle_col): 
		if particle_col.particles:
			delays = []
			count = len(particle_col.particles)		 
			while len(delays) < count: 
				diff = count - len(delays)
				#add remaining time delay
				if diff <= 3:
					delays = np.append(delays,self.SECONDS*diff/count)
				#add zeros to the remainder of the delay array
				if diff > 1 and diff <=3: 
					delays = np.concatenate((delays,np.zeros(diff-1)))
				else:
					group = np.random.randint(1,3)
					delays = np.concatenate((delays,np.zeros(group)))
					delays = np.append(delays,self.SECONDS*(group+1)/count)
			particle_col.delays = delays
			return particle_col 
	
	def write_metadata(self): 
		with open('../output/event_metadata.csv', 'wb') as fp:		
			a = csv.writer(fp, delimiter=',')
			data = [['Track', 'RPC'],[self.event.Tracks.size(), self.event.RPC.size()]]
			a.writerows(data)
		with open('../output/event_audio.csv', 'wb') as fp:
			a = csv.writer(fp, delimiter=',')
			data = [['BeatCount', 'Seconds'],[self.MAXBEATS, self.SECONDS]]
			a.writerows(data)
		with open('../output/event_audio.csv', 'wb') as fp:
			a = csv.writer(fp, delimiter=',')
			data = [['BeatCount', 'Seconds'],[self.MAXBEATS, self.SECONDS]]
			a.writerows(data)
		with open('../output/calo_beats.csv', 'wb') as fp:
			a = csv.writer(fp, quoting=csv.QUOTE_ALL)
			if self.event.LArHits.particles: 
				data = self.event.LArHits.getE()
				a.writerow(data)
		
		#upload CSV files to web
		if UPLOAD == True: 

			try: 
				imgname = "/var/www/sonification/sonification/static/img/recent_event_displays/JiveXML_" + str(self.event.event.RunNumber) + "_" + str(self.event.event.EventNumber) + ".png"
				print imgname
				subprocess.Popen("ssh cherston@discern.media.mit.edu 'cp " + imgname + " /var/www/sonification/sonification/static/img/physics.png'",shell=True)
			except: 
				pass

			try: 
				subprocess.Popen("scp ../output/event_metadata.csv cherston@discern.media.mit.edu:/var/www/sonification/sonification/static/event_metadata.csv",shell=True)
				subprocess.Popen("scp ../output/event_audio.csv cherston@discern.media.mit.edu:/var/www/sonification/sonification/static/event_audio.csv",shell=True)
				subprocess.Popen("scp ../output/calo_beats.csv cherston@discern.media.mit.edu:/var/www/sonification/sonification/static/calo_beats.csv",shell=True)
			except: 
				pass
			
	
	def wait_for_beat(self,t0):
		cur_time = time.time()-t0
		spb = self.SECONDS/self.MAXBEATS
		next_beat = int(cur_time/spb)*spb+spb
		#with open('../output/timingtest.csv', 'wb') as fp: 
		#	a = csv.writer(fp, quoting=csv.QUOTE_ALL)
		#		a.writerow(t0)
		#	a.writerow(cur_time)
		print "will sleep for: " + str(next_beat-cur_time) + "seconds"
		#time.sleep(next_beat-cur_time)

	 
