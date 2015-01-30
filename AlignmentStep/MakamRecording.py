# -*- coding: utf-8 -*-
'''
contains a Class 
Created on Mar 3, 2014

@author: joro
'''
from MakamScore import MakamScore
import subprocess
import os
from genericpath import isfile
import sys
from aetools import Error
from Utilz import loadTextFile, matchSections
import json

pathToSox = "/usr/local/bin/sox"
    
class MakamRecording:

    '''
    Logic to handle reading of audio section annotations, dividing into sections
    '''
    '''
    The size of self.sectionNames, self.beginTs, self.endTs, self.sectionIndices should be same
    
    '''

        
    def __init__(self, makamScore, pathToAudioFile, pathToLinkedSectionsFile):
       
       # the score of the piece
        self.makamScore = makamScore
        
        # wav file
        self.pathToAudiofile = pathToAudioFile
        self.pathToDividedAudioFiles= []
        
        
        # section timestamps,
        self.beginTs=[]
        self.endTs = []  
        
        # section names ordered as played in a recording
        self.sectionNamesSequence = []
        
        self.sectionIndices = []
        
        self._loadsectionTimeStamps( pathToLinkedSectionsFile)
        
        self.isChunkUsed  = []
        
        '''
        assigns a pointer (number) to each section Name from score
        '''
        
    
        return
    

    ##################################################################################

    ''' 
    @deprecated: 
    Handles the Division into sections. If 4 section names given for MakamScore, assumes the forth (nakarat) is melodic repetition of second but with different lyrics (2nakarat)  
    
#     '''
#     def assignSectionLyrics(self):
#         
#        # TODO: write cheker for score 
#         
#         flagMeyan = False
# 
#        # check section names and get lyrics from score. use index to map to Ts index
#         for index in range(len(self.sectionNamesSequence)):
#             
#             
#             currSectionName = self.sectionNamesSequence[index]
#             # remove 2 or 3 suffix
#             if str(currSectionName).endswith('2') or str(currSectionName).endswith('3'):
#                 currSectionName = currSectionName[0:-1]
#             # if meyan is gone, put 2 to signify  it is second nakarat (with different lyrics). Assumption: there is no third verse and third nakarat
#             if flagMeyan and currSectionName==MakamScore.sectionNamesSequence[1] and len(MakamScore.sectionNamesSequence)==4 :
#                 currSectionName='2' + currSectionName    
#                 
#             if currSectionName in MakamScore.sectionNamesSequence:
#                 self.sectionIndices[index] =   self.makamScore.sectionLyricsDict[currSectionName]
#                 if currSectionName == MakamScore.sectionNamesSequence[2]:
#                     flagMeyan = True
#             else:
#                 print "unknown section name: %s " ,  (currSectionName)
#                 self.sectionIndices[index] = ""
#                 
#             
#         return
            
        
        
       ##################################################################################
      
    ## loads timestamps from file .sectionAnno
    def _loadsectionTimeStamps(self, URILinkedSectionsFile):
        
        if not os.path.isfile(URILinkedSectionsFile):
                sys.exit("no file {}".format(URILinkedSectionsFile))
        
        ext = os.path.splitext(os.path.basename(URILinkedSectionsFile))[1] 
        if ext == '.txt' or ext=='.tsv':
            lines = loadTextFile(URILinkedSectionsFile)
            
            for line in lines:
                tokens =  line.split()
        
                if tokens[2] == 'gazel':
                    continue
                         
                self.beginTs.append(tokens[0])
                self.endTs.append(tokens[1])
                self.sectionNamesSequence.append(tokens[2])
                
                # WORKAROUND for section mapping. read mapping index from 4th field in .annotations file
                # sanity check: 
                if len(tokens) == 4:
                    self.sectionIndices.append(int(tokens[3]))
                    return
                    ######################
        elif ext == '.json':
                
                b = open (URILinkedSectionsFile)
                sectionLinks = json.load(b)
                b.close()
                
                sectionAnnos = sectionLinks['annotations']
                for sectionAnno in sectionAnnos:
                    self.beginTs.append(str(sectionAnno['time'][0]))
                    self.endTs.append(str(sectionAnno['time'][1]))
                    self.sectionNamesSequence.append( str(sectionAnno['name']) )
        else: 
            sys.exit("section annotation file {} has not know file extension.".format(URILinkedSectionsFile) )       
        # match automatically section names from sectionLinks to scoreSections 
        indices = []
        s1 = []
        for s in self.makamScore.sectionToLyricsMap:
            s1.append(s[0])
        self.sectionIndices = matchSections(s1, self.sectionNamesSequence, indices)        

       ##################################################################################
  
        
        # for given audio and ts divide audio into audio segments
    def divideAudio(self):
            
            for i in range(len(self.sectionNamesSequence)):
                if self.sectionNamesSequence[i] == 'aranagme':
                    continue
                
                filePathAndExt = os.path.splitext(self.pathToAudiofile)
                currBeginTs = self.beginTs[i].replace(".",'_')
                
                
                currEndTs = currEndTs = self.endTs[i].replace(".",'_')
                filePathDividedAudio = filePathAndExt[0] + '_' + str(self.sectionIndices[i]) + '_' + self.sectionNamesSequence[i] + '_from_' + currBeginTs + '_to_' + currEndTs + filePathAndExt[1] 
                
                self.pathToDividedAudioFiles.append(filePathDividedAudio)
                # make sure  sox (sox.sourceforge.net) is installed and call it  here with subprocess
                sectionDuration = float(self.endTs[i])-float(self.beginTs[i])
                pipe = subprocess.Popen([pathToSox, self.pathToAudiofile, filePathDividedAudio, 'trim', self.beginTs[i], str(sectionDuration)   ])
                pipe.wait()
            return
    '''
    if given wav file does not exists, assumes same file with .mp3 ext exists and converts it to wav
    '''    
    def mp3ToWav(self):
           # todo: convert to mp3 if not with Essentia
        baseNameAudioFile = os.path.splitext(self.pathToAudiofile)[0]
        
        if not os.path.isfile(self.pathToAudiofile):
             pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', baseNameAudioFile + '.mp3', self.pathToAudiofile])
             pipe.wait() 
    
    '''
    notUsed are chunks which will not be used in evaluation. 
    This used for now to exclude chunks where melodia has wrong pitch detection
    '''
    def markUsedChunks(self):
        
        self.isChunkUsed = [1] * len(self.pathToDividedAudioFiles)
        
        for index, pathToDividedAudioFile in enumerate(self.pathToDividedAudioFiles):
            if isfile( os.path.splitext(pathToDividedAudioFile)[0] +  ".notUsed"):
                self.isChunkUsed[index] = 0
        
        
    
if __name__ == '__main__':
        # only for unit testing purposes
        print "in Makam Recording"
 
        