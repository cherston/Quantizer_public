import xml.etree.ElementTree as ET
from functools import partial
from Particles import *
import ParticleFiller as PF

class XMLReader(object):
    """Class encapsulating the knowledge about reading the Masterclass XMLs and transfering the information into an event format"""
    def __init__(self):
        super(XMLReader, self).__init__()
        self.XMLTree = None
        self.Event = None
        self.Collections = dict()
    
    def clear(self):
        self.XMLTree = None
        self.Event = None
        self.Collections = dict()
    
    def parseFile(self, filename):
        tree = ET.parse(filename)
        self.XMLTree = tree.getroot()

    def getCollection(self, XMLTag, sgKey, storekey, GetterMethod):
        #check cache first
        collection = self.Collections.get(storekey)
        if collection is not None: return collection
        
        #see if node is available in input data
        Collections = self.XMLTree.findall(XMLTag)
        if not Collections: return ParticleCollection()

        #read out collections
        if sgKey == "":
            collection = GetterMethod(Collections[0])
            self.Collections[storekey] = collection
            return collection
        else:
            for coll in Collections:
                if sgKey in coll.attrib["storeGateKey"]:
                  collection = GetterMethod(coll)
                  self.Collections[storekey] = collection
                  return collection
        return ParticleCollection()

    def getEventInfo(self): return PF.getEventInfo(self.XMLTree)
    def getEtMiss(self):    return self.getCollection("TriggerInfo",    "",          "ETMis"     , PF.getEtMiss)
    def getRPC(self): 		return self.getCollection("RPC",        "RPC_Measurements", "RPC",           PF.getRPC) 
    
    
    def getVertices(self):  return self.getCollection("RVx",      "",                      "Vertices"  , PF.getVertices)
    def getMuons(self):     return self.getCollection("Muon",     "StacoMuonCollection",   "Muons"     , partial(PF.getMuons, tracks = self.getTracks()))
    def getElectrons(self): return self.getCollection("Electron", "ElectronCollection",    "Electrons" , partial(PF.getElectrons,tracks = self.getTracks()))
    def getJets(self):      return self.getCollection("Jet",      "AntiKt4TopoEMJets",     "Jets"      , PF.getJetCollection)

    def getTracks(self):   return self.getCollection("Track",   "Tracks",                  "Tracks"    , PF.getTracks)
    def getSegments(self): return self.getCollection("Segment", "ConvertedMBoySegments",   "Segments"  , PF.getMuonSegments)
    def getLArHits(self):  return self.getCollection("LAr",     "AllCalo",                 "LArHits"   , PF.getLArEntryCollection)
    def getHECHits(self):  return self.getCollection("HEC",     "AllCalo",                 "HECHits"   , PF.getHECEntryCollection)
    def getTILEHits(self): return self.getCollection("TILE",    "AllCalo",                 "TILEhits"  , PF.getTILEEntryCollection)
        
                
