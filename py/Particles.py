import math
from Utils import *
import XMLReader as reader 


class Event(object): 
	def __init__(self,event):
		self.Store = reader.XMLReader() 
		self.Store.parseFile(event)
		if self.Store.getEventInfo():
			self.event = self.Store.getEventInfo()
		if self.Store.getRPC():
			self.RPC = self.Store.getRPC() 
		if self.Store.getLArHits():
			self.LArHits = self.Store.getLArHits() 
		if self.Store.getHECHits(): 
			self.HECHits = self.Store.getHECHits() 
		if self.Store.getEtMiss(): 
			self.etmiss = self.Store.getEtMiss()
			print "LOOK: " + str(self.etmiss.getE())	
		if self.Store.getTracks().particles: 
			print "there are tracks: " + str(self.Store.getTracks().particles)
			self.Tracks = self.Store.getTracks()	
		else:
			self.Tracks  = ParticleCollection() 
				
class ParticleCollection(object): 
	def __init__(self,particles = []):
		self.particles = []
		self.delays = [] #delays controls the rate at which data should be read into the sound engine, based on the sorting parameter
		self.sparse_uniform_map = []
		
		for p in particles: 
			self.particles.append(p) 
			
	def __iter__(self): 
		return iter(self.particles) 
		
	def size(self):
		return len(self.particles)
	
	def getEta(self):
		return [p.Eta for p in self.particles]	
	
	def getPhi(self): 
		return [p.Phi for p in self.particles]	
	
	def getabsPhi(self): 
		return [abs(p.Phi) for p in self.particles]
	
	def getTheta(self): 
		return [p.Theta for p in self.particles] 
	
	def getE(self): 
		return [p.E for p in self.particles]	
	
	def getPt(self): 
		return [p.Pt for p in self.particles]	
	
	def getM(self): 
		return [p.M for p in self.particles]
	
	#Effective Sum only used for track collections 
	def getEffectiveSum(self): 
		return sum(self.getPt())	

		

	
class EtMiss(object):
    """Basic EtMiss for usage in the MasterclassReader code"""
    def __init__(self, name = "unknown EtMiss", etx = 0, ety = 0, et=0):
        super(EtMiss, self).__init__()
        self.setProperties(name,etx,ety,et) 
    
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
		
    def setProperties(self, name, etx, ety,et):
        self.Name = name
        self.E   = et
        self.Etx  = etx
        self.Ety  = ety
        self.Phi  = math.atan2(ety,etx) if etx == 0.0 and ety == 0.0 else 0
    
    def __str__(self):
        return "%s: et: %4.3f  etx: %4.3f  ety: %4.3f" % (self.Name, self.Et, self.Etx, self.Ety)

#===========================================================

class EventInfo(object):
    """EventInfo class holding information about the event"""
    def __init__(self, lumiblock = 0, eventNumber = 0, runNumber = 0):
        super(EventInfo, self).__init__()
        self.setProperties(lumiblock, eventNumber, runNumber)
    
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
    		
    def setProperties(self, lumiblock, eventNumber, runNumber):
        self.LumiBlock = lumiblock
        self.EventNumber = eventNumber
        self.RunNumber = runNumber

    def __str__(self):
        return "EventInfo: run: %i  event: %i  lumiblock: %i" % (self.RunNumber, self.EventNumber, self.LumiBlock)

#a=EventInfo()
#for prop in a: prop
#===========================================================

class Vertex(object):
    """docstring for Vertex"""
    def __init__(self, idNumber, primary, numtracks, tracks, z):
        super(Vertex, self).__init__()
        self.setProperties(idNumber, primary, numtracks, tracks, z)
    
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
  			
    def setProperties(self, idNumber, primary, numtracks, tracks, z):
        self.Id = idNumber
        self.Primary = primary
        self.NumTracks = numtracks
        self.TrackIds  = tracks
        self.Z = z
        
    def __str__(self):
        return "Vertex: id: %i\tprimary: %i\tnumTracks: %i\tz: %4.3f\tTrackIds: %s"\
        % (self.Id, self.Primary, self.NumTracks, self.Z, str(self.TrackIds))



#===========================================================

def findClosestTrack(particle, tracks, threshold):
    closestTrack = None
    mindeltaR = threshold
    for track in tracks:
      if Utils.deltaR(particle, track) < mindeltaR:
        closestTrack = track
        mindeltaR = Utils.deltaR(particle, track)
    return closestTrack

#===========================================================
class Electron(object):
	def __init__(self, en = 0, pt = 0, eta = 0, phi = 0, quality = "Unknown"):
		super(Electron, self).__init__()
		self.setProperties(pt,eta,phi,en)
		self.Quality = quality
		self.Pdg_id = 0
	
	def __iter__(self):
		for each in self.__dict__.keys():
			yield self.__getattribute__(each)
	
	def setProperties(self, pt, eta, phi,en):
		self.Pt= pt
		self.Eta = eta
		self.Phi = phi
		self.absPhi = abs(phi)
		self.E = en
	
	def getEta(self):
		return self.Eta
	
	def getE(self):
		return self.E
		
	def findClosestTrack(self, tracks, threshold):
		self.setTrack(findClosestTrack(self, tracks, threshold))
		
	def setTrack(self, track = None):
		self.Track = track
		if not track: return
		self.Pdg_id = int(11*track.Charge)

	def setHits(self, hits):
		if not hits: return
		self.Hits = hits
                    
	def __str__(self):
		return "Electron: id: %i\tpt: %4.3f\teta: %4.3f\tphi: %4.3f\tq: %i\td0: %4.3f\tz0: %4.3f\tisoPt: %4.3f"\
		% (self.Track.Id, self.Track.Pt, self.Track.Eta, self.Track.Phi, self.Track.Charge, self.Track.D0, self.Track.Z0)
        #self.Track.IsoPt [left out because returning error]   

#a = Electron(1,2,3,4)
#for prop in a: print prop      
#===========================================================

class Muon(object):
    """docstring for Muon"""
    def __init__(self, pt = 0, eta = 0, phi = 0, en = 0):
        super(Muon, self).__init__()
        self.setProperties(pt,eta,phi,en)
        self.Pdg_id = 0
        
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
	
    def setProperties(self, pt, eta, phi, en):
        self.Pt = pt
        self.Eta = eta
        self.Phi = phi
        self.absPhi = abs(phi)
        self.E = en

    def findClosestTrack(self, tracks, threshold):
      self.setTrack(findClosestTrack(self, tracks, threshold))

    def setTrack(self, track):
      self.Track = track
      if not track: return
      self.Pdg_id = int(13*track.Charge)

    def __str__(self):
        return "Muon: id: %i\tpt: %4.3f\teta: %4.3f\tphi: %4.3f\tq: %i\td0: %4.3f\tz0: %4.3f\tisoPt: %4.3f"\
        % (self.Track.Id, self.Track.Pt, self.Track.Eta, self.Track.Phi, self.Track.Charge, self.Track.D0, self.Track.Z0, self.Track.IsoPt)
        
#===========================================================

#===========================================================
class RPC(object): 
    def __init__(self, x, y, z):
        super(RPC, self).__init__()
        self.setProperties(x, y, z)
        
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
    
    def setProperties(self,x, y, z): 
    	self.x = x
    	self.y = y
    	self.z = z    	
    	self.r,self.Eta,self.Phi = cart_to_rap((self.x,self.y,self.z)) 
    	self.Theta = eta_to_theta(self.Eta)

    	
    	
    
#===========================================================

class Jet(object):
    """docstring for Jet"""
    def __init__(self, et, eta, phi, mass):
        super(Jet, self).__init__()
        self.setProperties(et, eta, phi, mass)
	
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
    
    def setProperties(self, et, eta, phi, mass):
        self.E = et
        self.Eta = eta
        self.Phi = phi
        self.M = mass
        self.absPhi = abs(phi)
        
    def __str__(self):
        return "Jet: Et: %4.3f\teta: %4.3f\tphi: %4.3f\tmass: %4.3f"\
        % (self.E, self.Eta, self.Phi, self.M)

#===========================================================

class Track(object):
    """docstring for Track"""
    def __init__(self, idNumber = -1, pt = 0, eta = 0, phi = 0, d0 = 0, z0 = 0,single_track_delay = 0.1):
        super(Track, self).__init__()
        self.setProperties(idNumber, pt, eta, phi, d0, z0)
	
    def __iter__(self): 
    	for each in self.__dict__.keys(): 
    		yield self.__getattribute__(each) 
    
    def size(self):
    	return len(self.particles)
    
    def setProperties(self, idNumber, pt, eta, phi, d0, z0):
        self.Id     = idNumber
        self.Pt     = pt
        self.Charge = cmp(pt,0)
        self.Eta    = eta
        self.Phi    = phi
        self.D0     = d0
        self.Z0     = z0
        self.E      = self.Pt * math.cosh(self.Eta)
        self.Theta = eta_to_theta(self.Eta)
        self.polyline_pt = self.generate_polyline()
       
        ## Added by J 
        self.IsoPt = 0
        self.ZtoPV = 0
    
    def generate_polyline(self): 
    	if abs(self.Pt) < 2:
    		num_points = int(abs(self.Pt) * 10) 
    	else: 
    		num_points = 20
    	
    	polyline_pt = np.linspace(0,self.Pt,num=num_points)
    	
    	#Not using for now, but just in case it's needed at some point#
    	polyline_eta = self.Eta * np.ones(num_points)
    	polyline_phi = self.Phi * np.ones(num_points) 
    	#x = i/num_points*self.Pt*math.Sin(self.Phi)*math.cos(self.Theta)
    	#y = i/num_points*self.Pt*math.Sin(self.Phi)*math.sin(self.Theta)
    	#z = i/num_points*math.cos(self.Phi)
    	#Not using for now, but just in case it's needed at some point#
    	
    	return polyline_pt 
			
			
		
    def computeIsolation(self, tracks, cone):
        pTOfTracksInCone = [track.Pt for track in tracks if self.trackInCone(track, 0.01, cone)]
        self.IsoPt = sum(pTOfTracksInCone)

    def trackInCone(self, track, minCone, maxCone):
        if abs(track.D0) > 0.25 or abs(track.Z0 - self.Z0) > 1: return False
        deltaR = DeltaR(self, track)
        if deltaR > maxCone or deltaR < minCone: return False
        return True

    def computeDistanceToPV(self, primVertex):
        return abs(self.Z0 - primVertex.Z)

    def __str__(self):
        return "Track: id: %i\tpt: %4.3f\teta: %4.3f\tphi: %4.3f\tq: %i\td0: %4.3f\tz0: %4.3f\tisoPt: %4.3f\tzToPV: %4.3f"\
        % (self.Id, self.Pt, self.Eta, self.Phi, self.Charge, self.D0, self.Z0, self.IsoPt, self.ZtoPV)


 #===========================================================

class LArEntry(object):
	def __init__(self, energy, eta, phi):
		super(LArEntry, self).__init__()
		self.setProperties(energy, eta, phi)
	
	def __iter__(self):
		for each in self.__dict__.keys():
			yield self.__getattribute__(each)  
	
	def setProperties(self, energy, eta, phi):
		self.E = energy
		self.Eta = eta
		self.Phi = phi
		self.absPhi = abs(phi)
		self.Theta = eta_to_theta(self.Eta)
		 
		
	def __str__(self):
		return "LArEntry: E: %4.3f\teta: %4.3f\tphi: %4.3f"\
		% (self.E, self.Eta, self.Phi)

 #===========================================================

class HECEntry(object):
    """docstring for HECEntry"""
    def __init__(self, energy, eta, phi):
    	super(HECEntry, self).__init__()
    	self.setProperties(energy, eta, phi)
    
    def __iter__(self): 
    	for each in self.__dict__.keys():
    		yield self.__getattribute__(each)
    		
    def setProperties(self, energy, eta, phi):
    	self.E = energy
    	self.Eta = eta
    	self.Phi = phi
    	self.absPhi = abs(phi)
    	self.Theta = eta_to_theta(self.Eta)
    	 
    def __str__(self):
    	return "HECEntry: E: %4.3f\teta: %4.3f\tphi: %4.3f"\
    	% (self.E, self.Eta, self.Phi)

# #===========================================================
#
# class TILEEntry(object):
#     """docstring for TILEEntry"""
#     def __init__(self, energy, eta, phi):
#         super(TILEEntry, self).__init__()
#         self.setProperties(energy, eta, phi)
#
#     def setProperties(self, energy, eta, phi):
#         self.E = energy
#         self.Eta = eta
#         self.Phi = phi
#
#     def __str__(self):
#         return "TILEEntry: E: %4.3f\teta: %4.3f\tphi: %4.3f"\
#         % (self.E, self.Eta, self.Phi)
    
#===========================================================

# class Event(object):
#     """docstring for Event"""
#     def __init__(self):
#         super(Event, self).__init__()
#         self.EtMiss = None
#         self.EventInfo = None
#         self.TrackCollection = None
#         self.VertexCollection = None
#         self.MuonSegmentCollection = None
#         self.MuonCollection = None
#         self.ElectronCollection = None
#         self.JetCollection = None
#         self.LArEntryCollection = None
#         self.HECEntryCollection = None
#         self.TILEEntryCollection = None
#
#     def checkValidity(self):
#         pass
#
#     def printEvent(self):
#         print self.EventInfo
#         print self.EtMiss
#         if self.TrackCollection is not None:
#             for track in self.TrackCollection: print track
#         if self.VertexCollection is not None:
#             for vertex in self.VertexCollection: print vertex
#         if self.MuonSegmentCollection is not None:
#             for muonsegment in self.MuonSegmentCollection: print muonsegment
#         if self.JetCollection is not None:
#             for jet in self.JetCollection: print jet
#         #if self.LArEntryCollection is not None:
#         #    for larentry in self.LArEntryCollection: print larentry
#         #if self.HECEntryCollection is not None:
#         #    for hecentry in self.HECEntryCollection: print hecentry
#         #if self.TILEEntryCollection is not None:
#         #    for tileentry in self.TILEEntryCollection: print tileentry
#         #print "=================================================="
            
#===========================================================      
            
# class PreparedEvent(object):
#     """docstring for PreparedEvent"""
#     #def __init__(self, arg):
#     def __init__(self, Event):
#         super(PreparedEvent, self).__init__()
#         #self.Event = Event
#         self.goodTracks     = None
#         self.goodPVTracks   = None
#         self.Muons          = None
#         self.Electrons      = None
#         self.Jets           = None
#         self.EtMiss         = Event.EtMiss
#
#     def printEvent(self):
#         print "=================================================="
#         print "GOOD TRACKS:"
#         for track in self.goodTracks: print track
#         print "=================================================="
#         print "GOOD TRACKS FROM PRIMARY VERTEX:"
#         for track in self.goodPVTracks: print track
#         print "=================================================="
#         print "MUONS:"
#         for muon in self.Muons: print muon
#         print "=================================================="
#         print "ELECTRONS:"
#         for electron in self.Electrons: print electron
#         print "=================================================="
#         print "NUMBER OF JETS: %i" % (len(self.Jets))
#         print "=================================================="
        
# #===========================================================
#
# class MuonSegment(object):
#     """docstring for MuonSegment"""
#     def __init__(self, eta, phi, numhits):
#         super(MuonSegment, self).__init__()
#         self.setProperties(eta, phi, numhits)
#
#     def setProperties(self, eta, phi, numhits):
#         self.Eta = eta
#         self.Phi = phi
#         self.NumHits = numhits
#
#     def __str__(self):
#         return "MuonSegment: eta: %4.3f\tphi: %4.3f\tnumHits: %i"\
#         % (self.Eta, self.Phi, self.NumHits)
#

 



