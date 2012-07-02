import os, shutil
import logging



HOME_WORKING = False

DIR_MAIN = "/Downloads/newsgroups/complete/TV"
    
    
#CMD_FR = "periscope -l fr"
#CMD_EN = "periscope -l en"
CMD_FR = "subliminal -l fr"
CMD_EN = "subliminal -l en"
CMD_CONV = "iconv --to-code=UTF-8"

NasDest = "/nas/Series/AAA_En_Cours"
destSeries = "/data/Video/Series_en_cours"

EN_EXT = "-en.srt"
FR_EXT = "-fr.srt"

MERGED_EXT = "-mg.srt"

TARGET = {

"Mentalist" : os.path.join(destSeries,'The mentalist Saison4'),
"Theory" : os.path.join(NasDest,'The Big Bang Theory S5'),
"Private" : os.path.join(destSeries,'private practice S5'),
"Fringe" : os.path.join(NasDest,'Fringe S4'),
"Desperate" : os.path.join(NasDest,'Desperate'),
"Alcatraz" : os.path.join(NasDest,'Alcatraz'),
"Interest" : os.path.join(destSeries,'POI'),
"House" : os.path.join(destSeries,'House_s8'),
#"Sherlock" : os.path.join(NasDest,'Sherlock'),

"How" : os.path.join(NasDest,'HIMYM'),
}


# Change value to test it from work
def initDataFromWork():
    
    global DIR_MAIN
    DIR_MAIN = u"C:\\tmp"


    
    ## Download Directory to move
    
    
    

class FolderAnalyse():

    directory = None
    aviName = None
    hasSubtitleFr = False
    hasSubtitleEn = False
    hasSubtitleMerged = False

    def __init__(self,dir):
        self.directory = dir
        self.analyseDir()

    def analyseDir(self):
        files = []
        subs = []
        for f in os.listdir(self.directory):
            if (f[-3:] == 'avi' and f[-10:] != 'sample.avi' and f[:6] != 'sample'):
                files.append(os.path.join(self.directory,f))
                self.aviName = os.path.join(self.directory,f)
            if (f[-4:] == '.srt'):
                subs.append(os.path.join(self.directory,f))


        if (len(files) == 0):
            logging.debug( " Avi File not found in %s" %self.directory)
            self.aviName = None
        elif (len(files) != 1):
            logging.debug( " Too many files found in %s " %self.directory)
            logging.debug(",".join(files))
            self.aviName = None
        else :

            if (self.aviName[:-4] + EN_EXT in subs):
                self.hasSubtitleEn = True
            if (self.aviName[:-4] + FR_EXT in subs):
                self.hasSubtitleFr = True
            if (self.aviName[:-4] + MERGED_EXT in subs):
                self.hasSubtitleMerged = True
            elif (self.aviName[:-4] + ".srt" in subs):
                self.hasSubtitleFr = True

    def convertion(self, file):         
        logging.debug(CMD_CONV + " \"%s\" > \"%s\"" %(file, file))
        return
        os.system(CMD_CONV + " \"%s\" > \"%s\"" %(file, file))


    def downloadSub(self, ext, extStr, cmd):
        if (self.aviName != None and not self.hasSubtitleFr) :             
            logging.info("Download subtitle %s for %s" % (extStr,self.aviName))            
            logging.debug(cmd + " \"" + self.aviName + "\"")
            
            os.system(cmd + " \"" + self.aviName + "\"")
            if (os.path.exists(self.aviName[:-4] + ".srt")):
                shutil.move(self.aviName[:-4] + ".srt", self.aviName[:-4] + ext)
                self.convertion(self.aviName[:-4] + ext)                
        else :
            if (self.aviName == None):
                logging.error("Avi file is not present " + self.directory)


    def downloadSubFr(self):
        self.downloadSub(FR_EXT,"fr",CMD_FR)
                
    def downloadSubEn(self):
        self.downloadSub(EN_EXT,"fr",CMD_EN)
                
    def moveToTarget(self, force = False):

        if (force or self.hasSubtitleFr or self.hasSubtitleEn):
        
            dest = self.findTargetDirectory()
            if (dest != None):
                logging.info( " Move directory %s to  %s" %(self.directory, dest))
                #print "todo"
                import shutil
                #print os.path.join(dest,os.path.basename(self.directory))
                dirOutput = os.path.join(dest,os.path.basename(self.directory)) 
                if ( os.path.exists(dirOutput)):
                    logging.debug("remove dir %s" %dirOutput)
                    shutil.rmtree(dirOutput)
                shutil.move(self.directory,dest)
            else :
                logging.error("Destination directory for %s not found" %(self.directory))

        else :
            if (force == False):
                logging.error("Sub file is not present in %s" %self.directory)


    def  convertionAll(self):
        if (self.hasSubtitleEn):
            self.convertion(self.aviName[:-4] + EN_EXT)

        if (self.hasSubtitleFr):
            self.convertion(self.aviName[:-4] + FR_EXT)

    def enFile(self):
        if (self.aviName != None):
            return self.aviName[:-4] + EN_EXT
        return None

    def frFile(self):
        if (self.aviName != None):
            return self.aviName[:-4] + FR_EXT
        return None

    def generateMerge(self):

        if (self.hasSubtitleEn and self.hasSubtitleFr and not self.hasSubtitleMerged):
            from mergesub import Merge
            mergeObject = Merge(self.enFile(), self.frFile())
            print "*************** Merge %s and %s \n" %(self.enFile, self.frFile())
            mergeObject.process(self.aviName[:-4] + MERGED_EXT)

    def do(self, moveToTarget = True):
	
        self.downloadSubFr()
        self.downloadSubEn()
        self.convertionAll()
#        self.generateMerge()
        if (moveToTarget):
            self.analyseDir()
            self.moveToTarget()

    def __str__(self):
        return "*****************\nDirectory value:\t\t%s\n Avi FileName:\t\t %s\nHas subtitle Fr En\t\t %s %s\n" %(self.directory, self.aviName, self.hasSubtitleFr , self.hasSubtitleEn)

    def findTargetDirectory(self):
        import re
        for pattern in TARGET.keys():
            if (re.search(pattern, self.directory) != None):
                return TARGET[pattern]
        return None
    
    
    
if (HOME_WORKING):
    
    folders = []
    
    
    for f in os.listdir(DIR_MAIN):
        fileD = os.path.join(DIR_MAIN,f)
        if (os.path.isdir(fileD)):
            folders.append(FolderAnalyse(fileD))
    
    # Analyse download directory
    for a in folders:
        a.moveToTarget()
    
    
    # Analyse Nas directory
    #folders = []
    
    for a in TARGET.values() :
        for b in os.listdir(a):
            if (b == 'Vu' or b == "@eaDir") :
                continue
            fileD = os.path.join(a , b)
            if (os.path.isdir(fileD)):
                fa = FolderAnalyse(fileD)
    #	    print fa
                fa.do(moveToTarget = False)
    
    print "done"



def moveFiles():
    
    logging.info("Move download files")
    
    folders = []        
    for f in os.listdir(DIR_MAIN):
        fileD = os.path.join(DIR_MAIN,f)
        if (os.path.isdir(fileD)):
            folders.append(FolderAnalyse(fileD))
    
    # Analyse download directory
    for a in folders:
        a.moveToTarget(force = True)
    

def downloadSubtitle():
    
    logging.info("Download subtitle")
    
    folders = []        
    for f in os.listdir(DIR_MAIN):
        fileD = os.path.join(DIR_MAIN,f)
        if (os.path.isdir(fileD)):
            folders.append(FolderAnalyse(fileD))
    
    # Analyse download directory
    for a in folders:
        #a.moveToTarget(force = True)
        a.downloadSubFr()
        a.downloadSubEn()

    
if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-m", "--move", action="store_true",  dest="move" ,help = "move files")
    parser.add_option("-d", "--debug",action="store_true",  dest="debug", default=False, help="debug information")
    parser.add_option("-w", "--work",action="store_false", dest="home", default=True , help="work datas")
    parser.add_option("-s", "--subtitle",action="store_true", dest="subtitle", default=False , help="download subtitle")
    
    (options, args) = parser.parse_args()

    if (options.debug):
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    else :
        logging.basicConfig(format='%(message)s', level=logging.ERROR)
        
    
    if (not options.home):        
        initDataFromWork()
    
    if (options.subtitle):
        downloadSubtitle()
    
    if (options.move):
        moveFiles()
        


