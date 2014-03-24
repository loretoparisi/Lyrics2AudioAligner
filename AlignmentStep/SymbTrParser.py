# -*- coding: utf-8 -*-
'''
Created on Mar 10, 2014
 contains a class 
 
@author: joro
'''
import codecs
import os
from utils.Utils import loadTextFile


'''
Parses lyrics from symbTr v 1.0. Sections from tsv file
TODO: take only section names from tsv file. parse sections from symbTr double spaces 
'''
class SymbTrParser(object):
  
    
    def __init__(self, pathToSymbTrFile, pathToTsvFile):
        '''
        Constructor
        '''
        # list of note number and syllables
        self.listSyllables =[]
        self._loadSyllables( pathToSymbTrFile)


        # section boundaries.                 #  triples of sectin name, start note, edn note 
        self.sectionboundaries = []
        self._loadSectionBoundaries(pathToTsvFile)
        
        # list of  section names and their lyrics
        self.sectionLyrics = []
   
   ##################################################################################
     
    '''
    load syllables from symbTr file. parse syllables
    '''
    def _loadSyllables(self, pathToSymbTrFile):
    
    
        allLines = loadTextFile(pathToSymbTrFile)
        
        # skip first line
        
        for line in allLines[1:]:
            line = line.replace(os.linesep,'')
            
            tokens = line.split("\t")
            
            if len(tokens) == 12:
                if tokens[11] != '.' and tokens[11] != 'SAZ' and tokens[11] != u'ARANAĞME':
        #           note number and syllable
                    tupleSyllable = int(tokens[0]), tokens[11]
                    
                    self.listSyllables.append(tupleSyllable)
            
     
   ##################################################################################

    def _loadSectionBoundaries(self, pathToTsvFile):
            
            allLines = loadTextFile(pathToTsvFile)

            for line in allLines[1:]:
                #  triples of sectin name, start note number, end note number 
                tokens = line.strip().split("\t")
                tmpTriplet = tokens[0], int(tokens[1]), int(tokens[2]) 
                self.sectionboundaries.append(tmpTriplet)
       
       
     ##################################################################################
   
    '''
    converts syllables to words using " " at end of syllable from SymbTr 
    at the same time divides them into given sections.
    '''  
    def syllablesToWords(self):
        
        indexSyllable = 0
        for currSectionBoundary in self.sectionboundaries:
            
            currEndNoteNumber = currSectionBoundary[2]
            currSectionLyrics = ""
            
            while (indexSyllable <= len(self.listSyllables)-1 # sanity check
                    and 
                    self.listSyllables[indexSyllable][0] <= currEndNoteNumber ):
                        currSectionLyrics = currSectionLyrics + self.listSyllables[indexSyllable][1]
                        indexSyllable += 1
            
            # double empty space marks section end, but we dont use it for now             
            currSectionLyrics = currSectionLyrics.strip()
            # record lyrics
            self.sectionLyrics.append(currSectionLyrics)
        
    

 ##################################################################################

if __name__ == "__main__":
    path1=  '/Volumes/IZOTOPE/sertan_sarki/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik.txt'
    path2= '/Volumes/IZOTOPE/sertan_sarki/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik.sections.tsv'    
    
    symbTrParser = SymbTrParser(path1, path2)
    symbTrParser.syllablesToWords()
