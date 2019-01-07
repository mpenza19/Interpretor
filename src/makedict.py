import copy, sys

# Lexicon POS tags
ADJ = "ADJ"
ADV = "ADV"
CONJ = "CONJ"
INTJlex = "INTERJ"
NOUNlex = "N"
NUM = "NUM"
PROPERlex = "N"
PREP = "PREP"
PRON = "PRON"
VERBlex = "V"
PART = "PART"
INDECL = [NUM, PREP, PART]



# UDPipe POS tags (where different from LatMor)
ADP = "ADP"
AUX = "AUX"
CCONJ = "CCONJ"
DET = "DET"
INTJudp = "INTJ"
NOUNudp = "NOUN"
PROPERudp = "PROPN"
SCONJ = "SCONJ"
VERBudp = "VERB"
X = "X"


PUNCT = "()[]/\\,;:.<>\'\"?"

class Word:
    def __init__(self, line):
        self.LINE = line
        self.LEMMA = self.lemma()
        self.POS = self.pos()
        self.GENDER = self.gender()
        self.INFO = self.info()
        self.DEF = self.def_short()


    def lemma(self):
        return self.LINE[0] 

    def pos(self):
        l = len(self.LINE)

        if l>1 and self.LINE[1] in INDECL: return self.LINE[1]
        if l>1 and self.LINE[1] == INTJlex: return INTJudp
        if l>1 and self.LINE[1] == CONJ: return CCONJ
        if l>2 and self.LINE[2] == NOUNlex: return NOUNudp
        if (l>3 and self.LINE[3] == ADJ) or (l>9 and self.LINE[9] == ADJ): return ADJ
        if l>4 and self.LINE[4] == VERBlex: return VERBudp

        #sys.stderr.write("POS error:" + str(self.LINE) + '\n')
        return None

    def gender(self):
        if self.POS == NOUNlex: return self.LINE[4]
        return None

    def info(self):
        return self.LEMMA, self.POS, self.GENDER

    def def_raw(self):
        return self.LINE[-1]

    def def_short(self):
        rawdef = self.def_raw()
        while '(' in rawdef or ')' in rawdef:
            start = rawdef.find(')')
            end = rawdef.find('(')
            rawdef = rawdef[:start] + rawdef[end+1:]

        cleandef = ""
        #print self.LEMMA, rawdef.split()
        for word in rawdef.split():
            if '/' in word:
                #print word, rawdef
                word = word[:word.find('/')]
                #print word
                
            cleandef += word + ' '
        
        #print self.LEMMA, cleandef.split(), '\n'

        if self.POS == VERBudp and cleandef.startswith("to "):
            cleandef = cleandef[3:]

        for i in range(len(cleandef)):
            if cleandef[i] in PUNCT:
                return cleandef[:i].strip()
        return None

def lexicon_lat2eng():
    with open("../../lexicon/DICTPAGE.RAW", "r") as f:
        lines = f.readlines()

    lex = dict()
    for line in lines:
        linecopy = copy.deepcopy(line).strip()

        line = [l.strip(',') for l in line.strip("#")[:line.index("::")].split()[:-2]]
        line.append(linecopy[linecopy.index("::")+3:])

        #print line

        word = Word(line)
        
        if word.LEMMA not in lex.keys():
            lex[word.LEMMA] = [word]
        else:
            lex[word.LEMMA].append(word)
            
    return lex

def lexicon_eng2lat():
    lat2eng = lexicon_lat2eng()
    eng2lat = dict()
    #print "STARTING"

    for (lemma, words) in lat2eng.iteritems():
        #print "LEMMA:", lemma
        for word in words:
            if word.DEF not in eng2lat.keys():
                eng2lat[word.DEF] = [word]
            else:
                eng2lat[word.DEF].append(word)
    
    return eng2lat


def print_lexicon(lex):
    for key, value in lex.iteritems():
        print key, '|', value.DEF

#mylexicon = lexicon()
#print_lexicon(mylexicon)