# -*- coding: utf-8 -*-

import codecs
import os
import logging


class SubElement:

    def __init__(self, start, end, text):
        self.timeStart = start
        self.timeEnd = end
        self.text = text

    def appendLine(self, text):
        text = text.lstrip().rstrip()
        if text != '':
            if self.text != '':
                self.text += "\n"
            self.text += text

    def __repr__(self):
        return self.text

class AdvancedSubStationAlphaWriter:

    def __init__(self, filename, subElements, regular, italic, size):
        logging.debug('Writing "' + filename + '"')
        self.fontRegular = regular
        self.fontItalic = italic
        self.fontSize = size
        self.filename = filename
        self.elements = subElements
        self.write()

    def write(self):
        f = open(self.filename, 'w')
        f.write(codecs.BOM_UTF8)
        f.write(self.getHeader())
        for e in self.elements:
            f.write(self.getLine(e))
        f.close()

    def getLine(self, element):
        start = self.getTime(element.timeStart)
        end = self.getTime(element.timeEnd)
        text = element.text.replace("\n", "\\N")
        font = "Regular"

        isItalic = text.find('<i>') != -1
        if isItalic:
            font = "Italic"
            text = text.replace("<i>", "").replace("</i>", "")

    #    print text
        import string
        i1 = string.find(text, '[', 0)
        i2 = string.find(text, ']', 0)
        lStr1 = text[ i1 + 1 : i2 ]
        i1 = string.find(text, '[', i2)
        i2 = string.find(text, ']', i1)
        lStr2 = text[i1 + 1 : i2]

        return "Dialogue: 0,{0},{1},{2},,0000,0000,0000,,{3}\nDialogue: 0,{4},{5},{6},,0000,0000,0000,,{7}\n".format(start, end, 'lang1', lStr1, start, end, 'lang2', lStr2)

    def getTime(self, t):
        ms = t % 1000
        t = (t - ms) / 1000
        s = t % 60
        t = (t - s) / 60
        m = t % 60
        h = (t - m) / 60

        ms /= 10
        return '{0:01}:{1:02}:{2:02}.{3:02}'.format(h, m, s, ms)

    def getHeader(self):
        return "[Script Info]\n" \
            + "ScriptType: V4.00+\n" \
            + "\n"                   \
            + "[V4+ Styles]\n"       \
            + "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" \
            + "Style: Regular," + self.fontRegular + "," + self.fontSize + ",&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,1,2,20,20,20,0\n" \
            + "Style: Italic," + self.fontItalic + "," + self.fontSize + ",&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,-1,0,0,100,100,0,0,1,1,1,2,20,20,20,0\n" \
            + "Style: lang1," + self.fontItalic + "," + self.fontSize + ",&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,-1,0,0,100,100,0,0,1,1,1,4,20,20,20,0\n" \
            + "Style: lang2," + self.fontItalic + "," + self.fontSize + ",&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,-1,0,0,100,100,0,0,1,1,1,2,20,20,20,0\n" \
            + "\n" \
            + "[Events]\n" \
            + "Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text\n"

class SubRipReader:

  def __init__(self, filename):
    logging.debug('Reading "' + filename + '"')
    self.filename = filename
    self.bomLength = 0
    self.encoding = 'utf-8'
    self.lines = []
    self.elements = []
    self.detectBomAndEncoding()
    self.read()
    self.parse()

  def detectBomAndEncoding(self):
    f = open(self.filename, 'r')
    begin = f.read(4)
    f.close()
    if begin.startswith(codecs.BOM_UTF8):
      self.encoding = 'utf-8'
      self.bomLength = 3
    elif begin.startswith(codecs.BOM_UTF16_LE):
      self.encoding = 'utf-16-le'
      self.bomLength = 2
    elif begin.startswith(codecs.BOM_UTF16_BE):
      self.encoding = 'utf-16-be'
      self.bomLength = 2
    elif begin.startswith(codecs.BOM_UTF32_LE):
      self.encoding = 'utf-32-le'
      self.bomLength = 4
    elif begin.startswith(codecs.BOM_UTF32_BE):
      self.encoding = 'utf-32-be'
      self.bomLength = 4

    if self.bomLength > 0:
      logging.debug('BOM detected! Encoding: ' + self.encoding)
    else:
      logging.debug('No BOM found. Using utf-8 as default encoding.')

  def read(self):
    if not self.read2():
      logging.debug('Fail to read the file with ' + self.encoding + '. Trying iso-8859-1.')
      self.encoding = 'iso-8859-1'
      self.read2()

  def read2(self):
    try:
      f = codecs.open(self.filename, 'r', self.encoding)
      self.lines = f.readlines()
      f.close()
      if len(self.lines) > 0 and self.bomLength > 0:
        self.lines[0] = self.lines[0].encode('utf-8').decode('utf-8-sig')
    except:
      return False
    return True

  def parse(self):
    el = None
    isJustNew = False
    nextCountReady = True
    count = 0
    emptySub = []
    for line in self.lines:
      l = line.encode('utf-8')    \
        .replace("\n", "")        \
        .replace("\r", "")
      if isJustNew:
        isJustNew = False
        nextCountReady = False
        times = l.split(' --> ')
        el.timeStart = self.parseTime(times[0])
        el.timeEnd = self.parseTime(times[1])
      elif nextCountReady and l.isdigit():
        count += 1
        logging.debug("Reading SRT # " + l + "\r")
        if int(l) != count:
          logging.warning("Bad SRT number! Found: #" + l + ", but should be #" + count)
        if el != None:
          if el.text == '':
            emptySub.append(count - 1)
          else:
            self.elements.append(el)
        el = SubElement(0, 0, '')
        isJustNew = True
      else:
        l = l.replace("", "œ")   \
          .replace("", "’")      \
          .replace("", "“")      \
          .replace("", "”")      \
          .replace("´´", '"')      \
          .replace("´", "'")       \
          .replace("....", "…")    \
          .replace("...", "…")     \
          .replace(". . .", "…")
        l = self.applyLanguageOnLine(l)
        el.appendLine(l)
        nextCountReady = True

    if (el != None):
      self.elements.append(el)

    logging.debug('Parsing complete: ' + str(len(self.elements)) + ' subtitles found!')
    logging.debug(str(len(emptySub)) + ' subtitles were empty: ' + str(emptySub))

  def parseTime(self, time):
    r1 = time.split(":")
    h = int(r1[0])
    m = int(r1[1])
    r2 = r1[2].split(',')
    s = int(r2[0])
    ms = int(r2[1])
    return ((h * 60 + m) * 60 + s) * 1000 + ms

  def applyLanguageOnLine(self, line):
    return line

class Srt2Ass:

    def __init__(self, srt, fregular, fitalic, fsize, delete, ass):
    #    ass = srt.replace('.srt', '.ass')
        subs = SubRipReader(srt)
        AdvancedSubStationAlphaWriter(ass, subs.elements, fregular, fitalic, fsize)
        if delete:
            logging.debug("Removing " + srt + "…")
            os.remove(srt)

'''
if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Convert SubRip (srt) files to Advanced Sub Station Alpha (ass) files.')
  parser.add_argument('file', metavar='file', nargs='*', help='the SubRip (srt) file')
  parser.add_argument('--font-regular', metavar='fontr', nargs='?', help='Name of the font to use for regular text. Default is "Cronos Pro".', default="Cronos Pro")
  parser.add_argument('--font-italic', metavar='fonti', nargs='?', help='Name of the font to use for italic text. Default is "Cronos Pro".', default="Cronos Pro")
  parser.add_argument('--font-size', metavar='fonts', nargs='?', help='Font\'s size for both regular and italic fonts. Default is 24.', default="24")
  parser.add_argument('--delete', '-d', action='store_true', help='delete the original SubRip (srt) file')
  parser.add_argument('--verbose', '-v', action='store_true', help='print information about the process')
  args = parser.parse_args()

  Console.verbose = args.verbose

  srtfiles = []
  if len(args.file) == 0:
    os.chdir(".")
    srtfiles = glob.glob("*.srt")
  elif len(args.file) == 1:
    os.chdir(".")
    srtfiles = glob.glob(args.file[0])
  else:
    srtfiles = args.file

  for srt in srtfiles:
    Srt2Ass(srt, args.font_regular, args.font_italic, args.font_size, args.delete)
'''
#Srt2Ass('toto.srt', "Cronos Pro","Cronos Pro", "24", False)
