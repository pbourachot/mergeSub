# -*- coding: utf-8 -*-
import sys,os
import re


def ufile(filename):
    try :
        return open(filename, 'U').read().decode('utf-8').strip()
    except :
        print "%s should be encoded in utf-8" % filename
        sys.exit()
        


def usage(msg = None):
    if (msg != None):
        print msg
    else :
        print "python mergesub.py subtitle1.srt subtitle2.srt [output.srt]"

def convert( time):
    h = int(time) / 3600
    m = (int(time) - h * 3600) / 60
    s = float(time) - h * 3600 - m * 60

    stringS = str(s).replace('.',',')
    return "%s:%s:%s" %(h,m,stringS)


class MergedPart:

    def __init__(self, number, start, stop , text):
        self.number = number
        self.start = start
        self.stop = stop
        self.text = text

    def __str__(self):
        return unicode("[MERGED]%s : %s\t\t: %s\t\t: %s" % (self.number, convert(self.start), convert(self.stop), self.text))

class SubPartList:

    def __init__(self, l, name = None):

        self.list = l
        self.name = name

    def __str__(self):
        if (self.name != None):
            return "%s \nSize %s" %(self.name, len(self.list))
        return "Size %s" %(len(self.list))


    def generateFile(self, fileName):


        import codecs
        fOut = codecs.open(fileName, 'w',encoding='utf-16')
        try :
            for a in self.list:
                fOut.write(str(a.number) + "\n")
                fOut.write("%s --> %s\n" %(convert(a.start), convert(a.stop)))
                fOut.write("%s\n" %(a.text))
                fOut.write("\n")
        finally:
            fOut.close()






class SubPart:

    def __init__(self, content):
        self.parts = content.splitlines()
        self.number = self.parts[0]
        self.start, self.stop = self.get_time(self.parts[1])
        self.text = ' '.join(self.parts[2:]).replace('\n',' ')
        self.type = 'TD'

    def __str__(self):
        return unicode("%s : %s\t\t: %s\t\t: %s" % (self.number, self.start, self.stop, self.text))

    def to_seconds(self, stamp):
        stamp = stamp.strip()
        hours, minutes, seconds, milliseconds = re.split('[,:]', stamp)
        hours, minutes, seconds, milliseconds = tuple([int(x) for x in (hours, minutes, seconds, milliseconds)])
        return (hours * 60 * 60 + minutes * 60 + seconds + (float(milliseconds)/1000))

    def get_time(self, stamp):
        start, stop = map(self.to_seconds, stamp.split('-->'))
        return start, stop


class Merge:

    def __init__(self, f1, f2):
        self.str1 = f1
        self.str2 = f2


    def merge(self, l1, l2):
        myList = []
        ll1 = l1.list
        ll2 = l2.list
        ll1.reverse()
        ll2.reverse()
        e1 = ll1.pop()
        e2 = ll2.pop()
        index = 1
        while (len(ll1) > 0 and len(ll2) >0):
            if (e1.start ) < (e2.start):
                if (e1.stop < e2.start):
                    myList.append(MergedPart(index, e1.start, e1.stop, "E1 " + e1.text))
                    e1 = ll1.pop()
                else :
                    myList.append(MergedPart(index, e1.start, max(e1.stop, e2.stop), "[" + e1.text +"][" + e2.text + "]"))
                    e1 = ll1.pop()
                    e2 = ll2.pop()
            else :
                if (e2.stop < e1.start):
                    myList.append(MergedPart(index, e2.start, e2.stop, "E2 " +e2.text))
                    e2 = ll2.pop()
                else :
                    myList.append(MergedPart(index, e2.start, max(e1.stop, e2.stop), "[" + e1.text +"][" + e2.text + "]"))
                    e1 = ll1.pop()
                    e2 = ll2.pop()

            index += 1


        return SubPartList(myList, "Merged")

    def process(self, fileName = None):

        file1Parts = SubPartList(self.get_parts(ufile(self.str1)), self.str1)
        file2Parts = SubPartList(self.get_parts(ufile(self.str2)), self.str2)


        a = self.merge(file1Parts, file2Parts)

        if (fileName != None):
            a.generateFile(fileName)
        else :            
            for elem in a.list:
                print elem




    



    def get_parts(self, content):
        return [SubPart(line) for line in re.split('\n\n+', content)]


# Main code
if __name__ == "__main__":

    if (len(sys.argv) > 2):
        srt1 = sys.argv[1]
        srt2 = sys.argv[2]
        output = None
        if (len(sys.argv) > 3):
            output = sys.argv[3]
        if (not os.path.exists(srt1)):
            usage(" %s is not existing." %srt1)
        elif (not os.path.exists(srt2)):
            usage(" %s is not existing." %srt2)
        else :

            mergeObject = Merge(srt1,srt2)
            mergeObject.process(output)
            if (output != None):
                print "%s file has been generated as merge of %s and %s" %(output, srt1, srt2)
                
                if (True):                
                    print "Generate Ass file from %s" %(output)
                    import srttossa
                    srttossa.Srt2Ass(output, "Cronos Pro","Cronos Pro", "24", False)

    else :
        usage()



