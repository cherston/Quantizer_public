import math
import xml.etree.ElementTree as ET
from Particles import *

"""This file encodes the rules for getting the different physical objects defined in Particles with the information
obtained from the XML."""

def getFloats(XMLNode, name):
    strvalues = XMLNode.find(name).text.replace("\n", " ").split(" ")
    return [float(x) for x in strvalues if x is not '']

def getInts(XMLNode, name):
    strvalues = XMLNode.find(name).text.replace("\n", " ").split(" ")
    return [int(x) for x in strvalues if x is not '']

def getStrings(XMLNode, name):
    strvalues = XMLNode.find(name).text.replace("\n", " ").split(" ")
    return [str(x) for x in strvalues if x is not '']
    

#===========================================================

def getEtMiss(XMLNode):
    name = XMLNode.attrib["storeGateKey"]
    et = float(XMLNode.find("energyEtMiss").text) 
    etx = float(XMLNode.find("energyEx").text)
    ety = float(XMLNode.find("energyEy").text)
    EtMissObject = EtMiss(name,etx,ety,et)
    return EtMissObject
    
#===========================================================

def getEventInfo(XMLNode):
    lumiblock = int(XMLNode.attrib['lumiBlock'])
    evtNumber = int(XMLNode.attrib['eventNumber'])
    runNumber = int(XMLNode.attrib['runNumber'])
    EventInfoObject = EventInfo(lumiblock, evtNumber, runNumber)
    return EventInfoObject

# #===========================================================
    
def getVertices(XMLNode):
    nVertices = int(XMLNode.attrib["count"])
    primaryVertex = getInts(XMLNode, "primVxCand")
    numTracks     = getInts(XMLNode, "numTracks")
    trackIds      = getInts(XMLNode, "tracks")
    Zs            = getFloats(XMLNode, "z")

    VertexCollection = []
    sumTracks = 0
    for i in range(nVertices):
        VertexCollection.append(Vertex(i, primaryVertex[i], numTracks[i], trackIds[sumTracks:(sumTracks + numTracks[i])], Zs[i]))
        sumTracks += numTracks[i]
    return VertexCollection

#===========================================================

def getElectrons(XMLNode, tracks):
    nElectrons = int(XMLNode.attrib["count"])
    pts     = getFloats(XMLNode, "pt")
    eta     = getFloats(XMLNode, "eta")
    phi     = getFloats(XMLNode, "phi")
    quality = getStrings(XMLNode, "isEMString")
    en = getFloats(XMLNode, "energy")  
    ElectronCollection = ParticleCollection(Electron(pt = pts[i], eta = eta[i], phi = phi[i], quality = quality[i],en=en[i]) for i in range(nElectrons))
    [electron.findClosestTrack(tracks,0.05) for electron in ElectronCollection]
    return ElectronCollection

#===========================================================

def getMuons(XMLNode, tracks):
    nMuons = int(XMLNode.attrib["count"])
    pts = getFloats(XMLNode, "pt")
    eta = getFloats(XMLNode, "eta")
    phi = getFloats(XMLNode, "phi")  
    en = getFloats(XMLNode, "energy")  
    MuonCollection = ParticleCollection(Muon(pts[i], eta[i], phi[i], en[i]) for i in range(nMuons))
    #print MuonCollection[0].getE()
    [muon.findClosestTrack(tracks, 0.05) for muon in MuonCollection]
    return MuonCollection

def getRPC(XMLNode):
    nRPC = int(XMLNode.attrib["count"])
    print "Rpc count: " + str(nRPC)
    xs = getFloats(XMLNode, "x")
    ys = getFloats(XMLNode, "y")
    zs = getFloats(XMLNode, "z")
    if nRPC: 
        RPCCollection = ParticleCollection(RPC(x = xs[i], y = ys[i], z = zs[i]) for i in range(nRPC))
    return RPCCollection
	
# #===========================================================

def getJetCollection(XMLNode):
    nJets = int(XMLNode.attrib["count"])
    ets    = getFloats(XMLNode, "et")
    etas   = getFloats(XMLNode, "eta")
    phis   = getFloats(XMLNode, "phi")
    masses = getFloats(XMLNode, "mass")
    
    JetCollection = ParticleCollection(Jet(ets[i], etas[i], phis[i], masses[i]) for i in range(nJets))
    return JetCollection
    
#===========================================================

def getTracks(XMLNode):
    nTracks = int(XMLNode.attrib["count"])
    ids  = getInts(XMLNode, "id")
    etas = [math.asinh(cottheta) for cottheta in getFloats(XMLNode, "cotTheta")]
    phis = getFloats(XMLNode, "phi0")
    pts  = getFloats(XMLNode, "pt")
    d0s  = getFloats(XMLNode, "d0")
    z0s  = getFloats(XMLNode, "z0")

    TrackCollection = ParticleCollection(Track(ids[i],pts[i], etas[i], phis[i],d0s[i], z0s[i]) for i in range(nTracks))

    return TrackCollection


 #===========================================================

# def getMuonSegments(XMLNode):
#     nSegments = int(XMLNode.attrib["count"])
#     etas     = [-math.log(math.tan(theta/2.0)) for theta in getFloats(XMLNode, "theta")]
#     phis     = getFloats(XMLNode, "phi")
#     numhits  = getInts(XMLNode, "numHits")
#
#     MuonSegmentCollection = [MuonSegment(etas[i], phis[i], numhits[i]) for i in range(nSegments)]
#     return MuonSegmentCollection
#
# #===========================================================
    

def getLArEntryCollection(XMLNode):
	nLArEntries = int(XMLNode.attrib["count"])
	energies = getFloats(XMLNode, "energy")
	etas     = getFloats(XMLNode, "eta")
	phis     = getFloats(XMLNode, "phi")

	LArEntryCollection = ParticleCollection(LArEntry(energies[i], etas[i], phis[i]) for i in range(nLArEntries))
	return LArEntryCollection

 #===========================================================

def getHECEntryCollection(XMLNode):
	nHECEntries = int(XMLNode.attrib["count"])
	energies    = getFloats(XMLNode, "energy")
	etas        = getFloats(XMLNode, "eta")
	phis        = getFloats(XMLNode, "phi")
	HECEntryCollection = ParticleCollection(HECEntry(energies[i], etas[i], phis[i]) for i in range(nHECEntries))
	return HECEntryCollection

# #===========================================================
#
# def getTILEEntryCollection(XMLNode):
#     nTILEEntries = int(XMLNode.attrib["count"])
#     energies = getFloats(XMLNode, "energy")
#     etas     = getFloats(XMLNode, "eta")
#     phis     = getFloats(XMLNode, "phi")
#     TILEEntryCollection = [TILEEntry(energies[i], etas[i], phis[i]) for i in range(nTILEEntries)]
#     return TILEEntryCollection
#
#
 