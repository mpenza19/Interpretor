# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# LatMor POS tags
ADJ = "ADJ"
ADV = "ADV"
CONJ = "CONJ"
INTJ = "INTJ"
NOUNlm = "N"
NUM = "NUM"
PROPERlm = "PN"
PREP = "PREP"
PRONlm = "PRO"
VERBlm = "V"
PART = "PART"
INDECL = [CONJ, INTJ, NUM, PREP, PART]

# UDPipe POS tags (where different from LatMor)
ADP = "ADP"
AUX = "AUX"
CCONJ = "CCONJ"
DET = "DET"
NOUNudp = "NOUN"
PRONudp = "PRON"
PROPERudp = "PROPN"
SCONJ = "SCONJ"
VERBudp = "VERB"
X = "X"


""" Did you ever read the documentation of os.popen() the Hackish?
I thought not. It's not a technique COS 333 would teach you.
It's a StackOverflow legend.... """
from os import popen

noun_declensions = (0, 1, 2, 3, 4, 5)
adj_declensions = (1, 3)
verb_conjugations = (0, 1, 2, 3, 4)
long_vowels = 'āēīōūȳ'.decode('utf-8')
vowels = 'aeiouy'

irreg_nouns = ('domus', 'locus', 'deus', 'balneus', 'bos', 'cherub', 'Iesus', 'Jesus')
irreg_verbs = ('sum', 'possum', 'volo', 'nolo', 'fero', 'eo', 'malo')

cardinals = ("unus", "una", "duo", "tres", "quattuor", "quinque", "sex", "septem", "octo", "novem", "decem", "decim", "viginti", "ginta", "centum")
ordinals = ("primus", "secundus", "tertius", "quartus", "quintus", "sextus", "septimus", "octavus", "nonus", "decimus", "cesimus", "gesimus", "centesimus")
numchars = "IVXLCDM" + "ivxlcdm"

genitive_triggers = ("of", "'s")
dative_triggers = ("for")
accusative_triggers = ("to", "toward", "towards", "into", "through", "before", "after", "around", "against", "between", "among", "within", "outside", "beyond", "across", "above", "over", "below", "near")



class Word:
    def __init__(self, wordinfo):
        self.index, self.form, self.lemma, self.pos, self.feats_str, self.parent_index, self.deprel, self.orig_lemma = wordinfo
        self.ignored = False
        self.ignore_articles()

        self.nodes, self.node_id = None, None
        self.parent, self.children, self.siblings = None, None, None
        self.prev, self.next = None, None
        

        #self.number = None
        #self.gender, self.case = None, None
        #self.deponent, self.inf, self.tense, self.voice = None, None, None, None
        #self.mood, self.number, self.person = None, None, None


        self.feats = (dict([f.split('=') for f in self.feats_str.split('|')])) if self.feats_str not in ["", "_"] else dict()
        self.latmor = Word.get_latmor_default(self.form) if self.form.endswith("que") or self.form.endswith("ve") or self.form.endswith("ne") else None

    def ignore_articles(self):
        if "PronType=Art" in self.feats_str or self.orig_lemma in ("a", "an", "the"): self.ignore()

    def ignore(self):
        self.ignored = True

    def is_ignored(self):
        return self.ignored

    def get_nodes(self):
        return self.nodes

    def get_node_id(self):
        return self.node_id

    def set_nodes_info(self, nodes, node_id):
        self.nodes = nodes
        self.node_id = node_id

    def update_attr(self, attr_str):
        attr_func_str = "get_"+attr_str
        old_val = getattr(self, attr_str)
        new_val = getattr(self, attr_func_str)()
        setattr(self, attr_str, new_val)
        #print "%s: %s --> %s" % (attr_str.upper(), old_val, getattr(self, attr_str))

    
    def update(self, in_handle_aux=False, exclusions=list()):
        #print "MAKING UPDATE ON:", self.lemma
        
        attr_list = [attr for attr in self.__dict__ if attr not in ("latmor", "get_latmor", "verb_form", "get_verb_form", "tense", "get_tense", "voice", "get_voice", "nodes", "node_id") and hasattr(self, "get_"+attr) and callable(getattr(self, "get_"+attr)) and attr not in exclusions]

        for myattr in attr_list: self.update_attr(myattr)
        
        if hasattr(self, "get_latmor"): self.update_attr("latmor")
        if hasattr(self, "handle_aux") and callable(getattr(self, "handle_aux")) and not in_handle_aux: self.handle_aux()

        if self.children:
            for child in self.children: child.update()

    def get_gender(self): pass
    def get_case(self): pass

    def get_wordinfo(self):
        index = self.index
        form = self.form
        lemma = self.lemma
        pos = self.pos
        feats_str = self.feats_str
        parent_index = self.parent_index
        deprel = self.deprel
        orig_lemma = self.orig_lemma

        return index, form, lemma, pos, feats_str, parent_index, deprel, orig_lemma

    @staticmethod
    def get_latmor_default(myform):
        
        # Try myform as is
        latmor_default = Word.__get_latmor_case(myform)
        if latmor_default: return latmor_default

        # Try capitalizing first letter (proper names etc.)
        myform_cap = myform[0].upper() + myform[1:] if len(myform) > 1 else myform.upper()
        latmor_default = Word.__get_latmor_case(myform_cap)
        if latmor_default: return latmor_default
        
        # Try lowercasing whole word (remove extraeous capitalizations)
        myform_lower = myform.lower()
        latmor_default = Word.__get_latmor_case(myform_lower)
        if latmor_default: return latmor_default
        
        # Give up
        return "*%s" % myform

    @staticmethod
    def __get_latmor_case(myform):
        with popen("echo '%s' | fst-mor LatMor/latmor-robust.a" % myform) as f:
            latmors = [line.strip().decode('utf-8') for line in list(f)[2:]]
        latmor_default = latmors[0]
        return latmor_default if not latmor_default.startswith("no result") else False

    @staticmethod
    def get_indiv_gen(mylatmor, word=None, resolve_alt=False):
        if mylatmor == "": return ""
        
        cmd = "echo '%s' | fst-mor LatMor/latmor-macron-ascii.a" % ("\n"+mylatmor) if resolve_alt else "echo '%s' | fst-mor LatMor/latmor-gen.a" % mylatmor
        with popen(cmd) as f: lines = [line.strip().decode('utf-8') for line in f]
        gen = lines[2] if NUM in mylatmor and len(lines) > 3 else lines[2]
        err_msg = "no result for "
        return '*'+gen[len(err_msg):] if gen.startswith(err_msg) else gen


    @staticmethod
    def get_all_latmors(myform, form_macronized=False):
        if form_macronized:
            with popen("echo '%s' | fst-mor LatMor/latmor-macron-ascii.a" % myform) as f:
                return [line.strip().decode('utf-8') for line in f]

        with popen("echo '%s' | fst-mor LatMor/latmor-robust.a" % myform) as f:
            return [line.strip().decode('utf-8') for line in f]

    def iscard(self):
        isnum = self.lemma in cardinals
        for c in cardinals: isnum = isnum or self.lemma.endswith(c)
        isnum = isnum and not self.isord() and not self.isnumeral()
        return isnum

    def isord(self):
        isnum = self.lemma in ordinals
        for o in ordinals: isnum = isnum or self.lemma.endswith(o)
        isnum = isnum and not self.iscard() and not self.isnumeral()
        return isnum

    def isnumeral(self):
        isnum = self.lemma in (self.lemma.upper(), self.lemma.lower())
        for c in self.lemma: isnum = isnum and c in numchars
        isnum = isnum and not self.isord() and not self.iscard()
        return isnum

    

class Noun(Word):
    def __init__(self, wordinfo):
        Word.__init__(self, wordinfo)

        self.pos = self.get_pos()
        self.gender = self.get_gender()
        
        self.case = self.get_case()
        self.number = self.get_number()
        self.person = self.get_person()
        
        self.latmor = self.get_latmor()    

    def get_pos(self):
        if self.pos == NOUNudp: return NOUNlm
        if self.pos == PROPERudp: return PROPERlm
        if self.pos == PRONudp: return PRONlm

        return self.pos

    def get_gender(self):
        if "Gender" in self.feats:
            gender = self.feats["Gender"].lower()
            if gender and ',' in gender: gender = "masc"
            return gender

        all_latmors = self.get_all_latmors(self.lemma)
        all_latmors = [l[l.find("<")+1:].replace(">", "").split("<") for l in all_latmors]

        if self.pos == NOUNlm:
            for l in all_latmors:
                if l[0] == NOUNlm:
                    default_latmor = l
                    return default_latmor[1] 
            return "masc"
            
        elif self.pos == PROPERlm:
            for l in all_latmors:
                if l[0] == NOUNlm:
                    default_latmor = l
                    return default_latmor[1]
            return "masc"

        elif self.pos == PRONlm:
            if "PronType" not in self.feats:
                for l in all_latmors:
                    if l[0] == NOUNlm:
                        default_latmor = l
                        return default_latmor[2]
                return "masc"
            
            ptudp = self.feats["PronType"]
            if ptudp == "Prs": ptlm = "pers"    # personal
            elif ptudp == "Int": ptlm = "quest" # interrogative/question
            elif ptudp == "Rel": ptlm = "rel"   # relative
            elif ptudp == "Dem": ptlm = "dem"   # demonstrative
            elif ptudp == "Ind": ptlm = "indef" # indefinite
            else:                ptlm = None

            if ptlm == "rel":
                if not self.parent: return "masc"

                if self.parent.deprel in ("acl:relcl", "nmod") and hasattr(self.parent.parent, "gender"):
                    return self.parent.parent.gender

                if self.parent.deprel == "root" or (self.parent.deprel == "nsubj" and self.parent.parent.deprel == "root"):
                    return "masc"

            return "masc"
        
        return "masc"
        

    def get_case(self):
        
        if self.deprel == "obj": return "acc"
        if self.deprel == "iobj": return "dat"
        if self.deprel in ("nmod:poss", "compound"): return "gen"

        if "PronType" in self.feats and self.feats["PronType"] == "Rel" and self.parent and hasattr(self.parent, "case"):
            return self.parent.case

        if not self.children:
            if self.deprel == "conj" and self.parent and hasattr(self.parent, "case"):
                return self.parent.get_case()
            
            if self.deprel == "nmod":
                return "gen"

            if self.deprel in ("obl", "acl:relcl"):
                return "abl"
            
            return "nom"

        for child in self.children:
            if child.deprel == "case":
                
                if child.orig_lemma in genitive_triggers:
                    child.ignore()
                    return "gen"

                if child.orig_lemma in dative_triggers and child.pos == PREP:
                    child.ignore()
                    return "dat"
                
                if child.orig_lemma in accusative_triggers:
                    return "acc"

                return "abl"

            elif child.deprel == "nmod":
                if child.orig_lemma in ("who", "whom", "whose"):
                    return "nom"
                return "gen"
        
        if self.parent and self.parent.__class__ == self.__class__:
            return self.parent.get_case()

        if self.deprel == "root": return "nom"
        
        return self.feats["Case"].lower() if "Case" in self.feats else "nom"

    def get_number(self):
        if "Number" in self.feats:
            if self.feats["Number"] == "Sing": return "sg"
            if self.feats["Number"] == "Plur": return "pl"
        
        if self.pos == PRONlm:
            if "PronType" not in self.feats:
                ptlm = None

            else:
                ptudp = self.feats["PronType"]
                if ptudp == "Prs": ptlm = "pers"    # personal
                elif ptudp == "Int": ptlm = "quest" # interrogative/question
                elif ptudp == "Rel": ptlm = "rel"   # relative
                elif ptudp == "Dem": ptlm = "dem"   # demonstrative
                elif ptudp == "Ind": ptlm = "indef" # indefinite
                else:                ptlm = None
            
            if ptlm == "rel" and self.parent and hasattr(self.parent, "number"):
                return self.parent.number

            return "sg"

    def get_person(self):
        return int(self.feats["Person"]) if "Person" in self.feats else 3

    def get_latmor(self):
        if self.deprel == "expl": return ""
        
        if self.pos in (NOUNlm, PROPERlm):
            return "%s<%s><%s><%s><%s>" % (self.lemma, self.pos, self.gender, self.number, self.case)

        if self.pos == PRONlm:
            ptlm = None
            if "PronType" in self.feats:
                ptudp = self.feats["PronType"]
                if ptudp == "Prs": ptlm = "pers"    # personal
                elif ptudp == "Int": ptlm = "quest" # interrogative/question
                elif ptudp == "Rel": ptlm = "rel"   # relative
                elif ptudp == "Dem": ptlm = "dem"   # demonstrative
                elif ptudp == "Ind": ptlm = "indef" # indefinite
            
            poss = "poss" if "Poss" in self.feats.keys() and self.lemma != "qui" else False
            pers = int(self.feats["Person"]) if "Person" in self.feats.keys() else False
            refl = "refl" if "Reflex" in self.feats.keys() else False

        

            if ptlm == "pers":
                if pers != 3:
                    if self.case == "nom": self.ignore()

                    if self.lemma == "nos": self.lemma = "ego"
                    if self.lemma == "vos": self.lemma = "tu"
                    
                    return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, ptlm, pers, self.number, self.case)

                elif refl:
                    return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, refl, pers, self.number, self.case)

                else:
                    ptlm = "dem"
                    return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, ptlm, self.gender, self.number, self.case)
            
            elif not poss:
                if self.case == "nom": self.ignore()
                return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, ptlm, self.gender, self.number, self.case)
            
            else:
                return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, poss, self.gender, self.number, self.case)

    @staticmethod
    def get_indiv_gen(mylatmor, word=None):
        gen = Word.get_indiv_gen(mylatmor, word=word)
        if not gen.startswith("*"): return gen
        
        if word:
            if word.pos == PROPERlm:
                new_latmor = word.latmor.replace(PROPERlm, NOUNlm)    
            else: # self.pos in (NOUNlm, PRONlm)
                new_latmor = word.latmor.replace(NOUNlm, PROPERlm)
            
            gen = Word.get_indiv_gen(new_latmor, word=word)
            return gen
        
        return gen



class Adj(Word):
    def __init__(self, wordinfo):
        Word.__init__(self, wordinfo)
    
        self.gender = self.get_gender()
        
        self.case = self.get_case()
        self.number = self.get_number()
        self.degree = "positive" if "Degree" not in self.feats or self.feats["Degree"] == "Pos" else "comparative" if self.feats["Degree"] == "Cmp" else "superlative" if self.feats["Degree"] == "Sup" else "positive"
        self.latmor = self.get_latmor()

    def get_gender(self):
        if "Gender" in self.feats and ',' not in self.feats["Gender"]:
            return self.feats["Gender"]

        if self.pos == NUM and self.deprel in ("nsubj", "nsubj:pass", "root"): return "neut"

        if self.deprel in ("amod", "det") and self.parent and hasattr(self.parent, "gender"):
            return self.parent.gender
        
        return "neut"


    def get_case(self):
        if self.parent and hasattr(self.parent, "case"):
            return self.parent.case
        
        return self.feats["Case"].lower() if "Case" in self.feats else "nom"

    def get_number(self):
        if "Number" in self.feats:
            if self.feats["Number"] == "Sing": return "sg"
            if self.feats["Number"] == "Plur": return "pl"
        
        if self.deprel in ("amod", "det") and self.parent and hasattr(self.parent, "number"):
            return self.parent.number

        return "sg"

    def get_latmor(self):
        if self.lemma == "suus" and self.siblings:
            for sib in self.siblings:
                if sib.pos == PRONlm and sib.deprel == "nmod:poss" and sib.lemma == "is":
                    sib.ignore()
                if sib.pos == PRONlm and sib.deprel == "nmod:poss" and sib.lemma in ("meus", "tuus", "noster", "vester"):
                    self.ignore()
        
        if self.lemma == "hic":
            return "%s<PRO><dem><%s><%s><%s>" % (self.lemma, self.gender, self.number, self.case)
        
        if self.lemma == "omnis":
            return "%s<ADJ><positive><%s><%s><%s>" % (self.lemma, self.gender, self.number, self.case)

        if self.lemma == "nullus":
            return "%s<PRO><adj><%s><%s><%s>" % (self.lemma, self.gender, self.number, self.case)

        if self.iscard():
            if self.lemma in ("unus", "una", "duo", "tres"):
                return "%s<%s><%s><%s><%s>" % (self.lemma, NUM, self.gender, self.number, self.case)
            else:
                return "%s<%s><%s>" % (self.lemma, NUM, "card")

        elif self.isord():
            return "%s<%s><%s><%s><%s><%s>" % (self.lemma, NUM, "ord", self.gender, self.number, self.case)

        elif self.isnumeral():
            return "%s<%s><%s><%s>" % (self.lemma, NUM, "card", "dig")

        poss = "poss" if "Poss=Yes" in self.feats_str else None
        if poss:
            return "%s<%s><%s><%s><%s><%s>" % (self.lemma, PRONlm, poss, self.gender, self.number, self.case)

        return "%s<%s><%s><%s><%s><%s>" % (self.lemma, ADJ, self.degree, self.gender, self.number, self.case)

        
class Adv(Word):
    def __init__(self, wordinfo):
        Word.__init__(self, wordinfo)

        self.lemma = "malus" if self.lemma == "pessime" else self.lemma
        self.degree = "NA" if "Degree" not in self.feats else "positive" if self.feats["Degree"] == "Pos" else "comparative" if self.feats["Degree"] == "Cmp" else "superlative" if self.feats["Degree"] == "Sup" else "positive"
        self.latmor = self.get_latmor()

    def get_latmor(self):
        latmor = "%s<%s><%s>" % (self.lemma, ADV, self.degree) if self.degree != "NA" else "%s<%s>" % (self.lemma, ADV)
        if self.lemma in ["bonus", "malus"]: latmor = "%s<%s><%s><%s>" % (self.lemma, ADJ, self.degree, ADV)
        return latmor

class Verb(Word):
    def __init__(self, wordinfo):
        Word.__init__(self, wordinfo)

        self.deponent = self.is_deponent()
        self.verb_form = self.get_verb_form()
        self.inf = self.get_inf()
        self.tense = self.get_tense()
        self.mood = self.get_mood()
        self.number = self.get_number()
        self.person = self.get_person()
        self.voice = self.get_voice()
        self.case = self.get_case()
        self.gender = self.get_gender()
        self.handle_aux()
        self.latmor = self.get_latmor()

    def is_deponent(self):
        return self.lemma.endswith("or")

    def get_verb_form(self):
        if "VerbForm" not in self.feats: return "Fin"
        if self.feats["VerbForm"] == "Fin": return "Fin"
        if self.feats["VerbForm"] in ("Part", "Ger"): return "Part"
        if self.feats["VerbForm"] == "Inf": return "Inf"
        return "Fin"

    def get_inf(self):  
        # Irregular cases due to LatMor
        if self.form.startswith("repuli"):
            self.form = "repp" + self.form[3:]
            self.lemma = "repello"
            return "repellere"

        lines = []
        with popen("echo '%s' | fst-mor LatMor/latmor-robust.a" % self.lemma) as f:
            for line in f: lines.append(line)

        if len(lines[2:]) == 1 and lines[2].startswith("no result"):
            return self.lemma

        lines = [l.strip().replace('>', '').split('<') for l in lines[2:]]
        for line in lines:
            if not self.deponent and line[1] == 'V' and len(line) >= 5 and line[4] != "deponens": return line[0]
            if self.deponent and line[1] == 'V' and len(line) >= 5 and line[4] == 'deponens': return line[0]

        for line in lines:
            if "deponens" in line: self.deponent = True

            if self.deponent and line[1] == 'V' and len(line) >= 5 and line[4] == 'deponens': return line[0]

        return self.lemma
    
    def get_tense(self):
        # Participles are special case
        if self.verb_form == "Part":
            if "Tense" in self.feats:
                tense = self.feats["Tense"]
            else:
                return "perf"

            if tense == "Pres": return "pres"       # present
            if tense == "Fut":  return "future"     # future
            if tense == "Past": return "perf"       # past (default to PERFECT for participles)

            return "perf"
        
        # Non-participle cases
        if "Tense" in self.feats:
            tense = self.feats["Tense"]
        else:
            return "pres"

        if "Aspect" in self.feats and self.feats["Aspect"] == "Perf":
            if tense == "Past": return "perf"       # perfect
            if tense == "Fut":  return "futureII"   # future perfect

        if "Aspect" in self.feats and self.feats["Aspect"] == "Imp":
            if tense == "Past": return "imperf"     # imperfect
        
        if "Aspect" not in self.feats:
            if tense == "Pres": return "pres"       # present
            if tense == "Pqp":  return "pqperf"     # pluperfect
            if tense == "Fut":  return "futureI"    # future
            if tense == "Past": return "imperf"     # past (default to imperfect)

        return "pres"

    def get_voice(self):

        # Participles are special case
        if self.verb_form == "Part":
            if self.inf == "fieri": return "active"
        
            if self.deponent: return "deponens"
            
            voice = self.feats["Voice"] if "Voice" in self.feats else "Pass"
            
            if voice == "Act":  return "active"
            if voice == "Pass": return "passive"

            return "passive" if self.tense == "perf" else "active"

        # Non-participle cases
        if self.inf == "fieri": return "active"
        
        if self.deponent: return "deponens"
        
        voice = self.feats["Voice"] if "Voice" in self.feats else "Act"
        
        if voice == "Act":  return "active"
        if voice == "Pass": return "passive"

        return "active"

    def get_mood(self):
        if self.verb_form == "Fin":
            if self.deprel in ("ccomp", "advcl") and self.tense != "futureI": return "subj"

            mood = self.feats["Mood"] if "Mood" in self.feats else "Ind"
            
            if mood == "Ind": return "ind"
            if mood == "Sub": return "subj"
            if mood == "Imp": return "imp"
            
            return "ind"
        
        # Only finite verbs have mood
        return None

    def get_number(self):
        if self.verb_form == "gerundivum":
            return self.number
        
        if self.verb_form == "Fin":
            if self.deprel in ("aux", "aux:pass") and self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "number") and sib.deprel in ("nsubj", "nsubj:pass") and sib.number: 
                        return sib.number
            
            if self.deprel in ("acl:relcl", "aux", "aux:pass") and self.parent and hasattr(self.parent, "number") and self.parent.number:
                return self.parent.number

            if self.deprel == "advcl" and self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "number") and sib.deprel == "obj" and sib.number: 
                        return sib.number

            if self.children:
                for child in self.children:
                    if child.deprel in ("nsubj", "nsubj:pass"):
                        if hasattr(child, "number") and child.number: 
                            return child.number

            if "Number" in self.feats:
                number = self.feats["Number"]
                if number == "Sing": return "sg"
                if number == "Plur": return "pl"

            return "sg"

        if self.verb_form == "Part":
            if self.children:
                for child in self.children:
                    if child.deprel in ("nsubj", "nsubj:pass") and hasattr(child, "number"):
                        return child.number
            
            if self.deprel == "acl" and self.parent and hasattr(self.parent, "number"):
                return self.parent.number

            if self.deprel == "advcl" and self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "number") and sib.deprel == "obj": 
                        return sib.number

            if self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "number"): 
                        return sib.number
            
            if "Number" in self.feats:
                if self.feats["Number"] == "Sing": return "sg"
                if self.feats["Number"] == "Plur": return "pl"
            
            return "sg"

        # Only finite verbs and participles have number    
        return None

    def get_person(self):
        if "Person" in self.feats:
            return int(self.feats["Person"])
        
        if self.parent and hasattr(self.parent, "person") and self.deprel == "acl:relcl" and self.parent.deprel in ("nsubj", "nsubj:pass"):
            return self.parent.person

        if not self.children:
            return 3

        for child in self.children:
            if child.deprel in ("nsubj", "nsubj:pass") and hasattr(child, "person") and child.person:
                return child.person
                
        return 3            

    def get_gender(self):
        if self.pos == AUX:
            if self.siblings:
                for sib in self.siblings:
                    if sib.deprel in ("nsubj", "nsubj:pass") and hasattr(sib, "gender"):
                        return sib.gender
        
        if self.verb_form == "Part":

            if self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "case") and sib.case == self.case and hasattr(sib, "gender"): 
                        return sib.gender
                        
            if self.deprel == "advcl" and self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "gender") and sib.deprel == "obj": 
                        return sib.gender

            if self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "gender"): 
                        return sib.gender
                        
            if self.deprel in ("acl", "acl:relcl") and self.parent and hasattr(self.parent, "gender"):
                return self.parent.gender

            if self.children:
                for child in self.children:
                    if hasattr(child, "case") and child.case == self.case and hasattr(child, "gender"):
                        return child.gender
            
            if self.children:
                for child in self.children:
                    if hasattr(child, "gender"):
                        return child.gender

            
            
            return self.feats["Gender"].lower() if "Gender" in self.feats else "neut"

        # Only participles have gender
        return None
        
    def get_case(self):
        if self.verb_form == "Part":
            if self.deprel == "acl" and self.parent and hasattr(self.parent, "case"):
                return self.parent.case

            if self.deprel == "advcl" and self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "case") and sib.deprel == "obj": 
                        return sib.case
            
            if self.children:
                for child in self.children:
                    if child.deprel in ("nsubj", "nsubj:pass") and hasattr(child, "case"):
                        return child.case

            if self.siblings:
                for sib in self.siblings:
                    if hasattr(sib, "case"): 
                        return sib.case

            if self.parent and hasattr(self.parent, "case"):
                return self.parent.case
            
            return self.feats["Case"].lower() if "Case" in self.feats else "nom"

        # Only participles have case; default to nom
        return "nom"

    def handle_aux(self):
        if not self.children: return
        
        num_aux_children = 0
        for child in self.children:
            if child.deprel in ("aux", "aux:pass"):
                num_aux_children += 1
            if child.deprel == "mark" and child.orig_lemma == "to":
                child.ignore()

        if num_aux_children == 0 and self.deprel not in ("aux", "aux:pass"): 
            if self.verb_form != "Inf": pass
            
            for child in self.children:
                if child.deprel == "cop" and child.orig_lemma == "be" and child.next.deprel == "mark" and child.next.orig_lemma == "to":
                    self.verb_form = "Part"
                    self.tense = "future"
                    self.voice = "active"

                    self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                    child.next.ignore()
                    break

            if self.orig_lemma == "have" and self.prev and (self.prev.orig_lemma == "to" or (self.prev.prev and self.prev.prev.orig_lemma == "to" and self.prev.orig_lemma == "not")):    
                for child in self.children:
                    if hasattr(child, "verb_form") and child.verb_form == "Part":
                        myverbform = "Inf"
                        myvoice = "active"
                        mytense = "perf"

                        if child.children:
                            mygrandchild = None
                            for grandchild in child.children:
                                if grandchild.deprel == "aux:pass" and grandchild.orig_lemma == "be":
                                    myvoice = "passive"
                                    myverbform = "Part"
                                    mygrandchild = grandchild
                                    break
                        

                        self.pos = VERBlm
                        self.orig_lemma = child.orig_lemma
                        self.lemma = child.lemma
                        self.verb_form = myverbform
                        self.tense = mytense
                        self.voice = myvoice
                        self.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice"])

                        if myvoice == "passive":
                            child.pos = VERBlm
                            child.orig_lemma = "be"
                            child.lemma = "esse"
                            child.verb_form = "Inf"
                            child.tense = "pres"
                            child.voice = "active"
                            if mygrandchild: mygrandchild.ignore()
                        else:
                            child.ignore()
                            
                        child.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice"])
                        break

          

        elif num_aux_children == 1:
            if self.verb_form == "Inf":
                for child in self.children:
                    if child.deprel == "aux": 
                        
                        if child.orig_lemma in ("will", "shall"):
                            #print "UPDATING FUTURE INDICATIVE"
                            self.verb_form = "Fin"
                            self.tense = "futureI"
                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense"])
                            child.ignore()
                            break

                        elif self.deprel not in ("ccomp", "advcl") and child.orig_lemma == "would":
                            #print "UPDATING IMPERFECT INDICATIVE"
                            self.verb_form = "Fin"
                            self.tense = "imperf"
                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense"])
                            child.ignore()
                            break

                        elif self.deprel in ("ccomp", "advcl") and child.orig_lemma == "may":
                            #print "UPDATING PRESENT SUBJUNCTIVE"
                            self.verb_form = "Fin"
                            self.tense = "pres"
                            self.mood = "subj"
                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood"])
                            child.ignore()
                            break

                        elif self.deprel in ("ccomp", "advcl") and child.orig_lemma in ("might", "would"):
                            #print "UPDATING IMPERFECT SUBJUNCTIVE"
                            self.verb_form = "Fin"
                            self.tense = "imperf"
                            self.mood = "subj"
                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood"])
                            child.ignore()
                            break


            elif self.verb_form == "Part":
                for child in self.children:
                    if child.deprel in ("aux", "aux:pass"):

                        if child.orig_lemma == "have":
                            self.verb_form = "Fin"

                            if child.tense == "pres":
                                self.tense = "perf"
                            elif child.tense == "imperf":
                                self.tense = "pqperf"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense"])
                            child.ignore()
                            break

                        elif child.orig_lemma == "be" and self.deprel in ("ccomp", "advcl") and child.verb_form == "Inf":
                            self.verb_form = "Fin" 
                            self.tense = "pres"
                            self.mood = "subj"
                            self.voice == "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood", "voice"])
                            child.ignore()
                            break
                        
                        
                        elif child.orig_lemma == "be" and self.deprel not in ("ccomp", "advcl", "xcomp") and child.prev and child.prev.deprel == "mark" and child.prev.orig_lemma == "to":
                            aux_tense = child.tense
                            
                            child.verb_form = "Part"
                            child.orig_lemma = self.orig_lemma
                            child.lemma = self.lemma
                            child.tense = "perf"
                            child.voice = "passive"
                            child.number = self.number
                            child.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice", "number"])
                            child.verb_form = "gerundivum"
                            #child.latmor = child.get_latmor()
                            child.update(in_handle_aux=True, exclusions=["number"])

                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.tense = aux_tense
                            self.voice = "active"
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "tense", "voice"])
                           
                            #child.ignore()
                            child.prev.ignore()
                            break

                        elif child.orig_lemma == "be" and self.deprel not in ("ccomp", "advcl") and child.prev and child.prev.deprel == "mark" and child.prev.orig_lemma == "to":
                            self.verb_form = "Inf"
                            self.tense = "pres"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                            child.ignore()
                            break
                            
                        elif child.orig_lemma == "be" and self.deprel not in ("ccomp", "advcl", "xcomp"):
                            self.verb_form = "Fin"
                            self.voice = "passive"

                            if child.tense == "pres":
                                self.tense = "pres"
                            elif child.tense == "imperf":
                                self.tense = "imperf"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                            child.ignore()
                            break

        elif num_aux_children == 2: 
            if self.verb_form == "Part":
                for child1 in self.children[:-1]:
                    child2 = child1.next if child1.next.orig_lemma != "not" else child1.next.next

                    if child1.deprel == "aux" and child2.deprel == "aux":
                        if child1.orig_lemma in ("will", "shall") and child2.orig_lemma == "have":
                            self.verb_form = "Fin"
                            self.tense = "futureII"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense"])
                            child1.ignore()
                            child2.ignore()
                            break

                        elif child1.orig_lemma == "may" and child2.orig_lemma == "have":
                            self.verb_form = "Fin"
                            self.tense = "perf"
                            self.mood = "subj"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood"])
                            child1.ignore()
                            child2.ignore()
                            break

                        elif child1.orig_lemma in ("might", "would") and child2.orig_lemma == "have":
                            self.verb_form = "Fin"
                            self.tense = "pqperf"
                            self.mood = "subj"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood"])
                            child1.ignore()
                            child2.ignore()
                            break

                    elif child1.deprel == "aux" and child2.deprel == "aux:pass":
                        if self.deprel in ("ccomp", "advcl") and child1.orig_lemma == "may" and child2.orig_lemma == "be" and child2.verb_form == "Inf":
                            self.verb_form = "Fin"
                            self.tense = "pres"
                            self.mood = "subj"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood", "voice"])
                            child1.ignore()
                            child2.ignore()
                            break

                        elif self.deprel in ("ccomp", "advcl") and child1.orig_lemma in ("might", "would") and child2.orig_lemma == "be" and child2.verb_form == "Inf":
                            self.verb_form = "Fin"
                            self.tense = "imperf"
                            self.mood = "subj"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "mood", "voice"])
                            child1.ignore()
                            child2.ignore()
                            break
                        
                        elif child1.orig_lemma == "would" and child2.orig_lemma == "be":
                            self.verb_form = "Fin"
                            self.tense = "imperf"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                            child1.ignore()
                            child2.ignore()
                            break

                        elif child1.orig_lemma in ("will", "shall") and child2.orig_lemma == "be":
                            self.verb_form = "Fin"
                            self.tense = "futureI"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                            child1.ignore()
                            child2.ignore()
                            break

                        elif child1.orig_lemma == "have" and child2.orig_lemma == "be":
                            aux_tense = child1.tense
                            
                            child1.verb_form = "Part"
                            child1.orig_lemma = self.orig_lemma
                            child1.lemma = self.lemma
                            child1.tense = "perf"
                            child1.voice = "passive"
                            child1.gender = self.gender
                            
                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.tense = aux_tense
                            self.voice = "active"

                            child1.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice"])
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "tense", "voice"])
                            child2.ignore()
                            break

                        elif child1.orig_lemma == "must" and child2.orig_lemma == "be":
                            aux_tense = child2.tense
                           
                            child2.verb_form = "Part"
                            child2.orig_lemma = self.orig_lemma
                            child2.lemma = self.lemma
                            child2.tense = "perf"
                            child2.voice = "passive"
                            child2.number = self.number
                            
                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.tense = aux_tense
                            self.voice = "active"
                            
                            child2.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice", "number"])
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "tense", "voice"])
                            
                            child2.verb_form = "gerundivum"
                            child2.update(in_handle_aux=True, exclusions=["number"])

                            child1.ignore()
                            break
                            

                        elif child2.orig_lemma == "be":
                            self.verb_form = "Inf"
                            self.tense = "pres"
                            self.voice = "passive"

                            self.update(in_handle_aux=True, exclusions=["verb_form", "tense", "voice"])
                            child2.ignore()
                            break

        elif num_aux_children == 3:
            if self.verb_form == "Part":
                for child1 in self.children[:-2]:
                    child2 = child1.next if child1.next.orig_lemma != "not" else child1.next.next
                    child3 = child2.next

                    if child1.deprel == "aux" and child2.deprel == "aux" and child3.deprel == "aux:pass":
                        if child1.orig_lemma == "may" and child2.orig_lemma == "have" and child3.orig_lemma == "be":
                            child2.verb_form = "Part"
                            child2.orig_lemma = self.orig_lemma
                            child2.lemma = self.lemma
                            child2.tense = "perf"
                            child2.voice = "passive"
                            self.case = self.get_case()
                            child2.mood = self.get_gender()
                            
                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.mood = "subj"
                            self.tense = "pres"
                            self.voice = "active"
                            
                            child2.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "gender"])
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "mood", "tense"])
                            child1.ignore()
                            child3.ignore()
                            break

                        elif child1.orig_lemma in ("might", "would") and child2.orig_lemma == "have" and child3.orig_lemma == "be":
                            child2.verb_form = "Part"
                            child2.orig_lemma = self.orig_lemma
                            child2.lemma = self.lemma
                            child2.tense = "perf"
                            child2.voice = "passive"
                            self.case = self.get_case()
                            child2.mood = self.get_gender()
                            
                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.mood = "subj"
                            self.tense = "imperf"
                            self.voice = "active"
                            
                            child2.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "gender"])
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "mood", "tense"])
                            child1.ignore()
                            child3.ignore()
                            break

                        elif child1.orig_lemma in ("will", "shall") and child2.orig_lemma == "have" and child3.orig_lemma == "be":
                            child2.verb_form = "Part"
                            child2.orig_lemma = self.orig_lemma
                            child2.lemma = self.lemma
                            child2.tense = "perf"
                            child2.voice = "passive"
                            child2.mood = "ind"
                            self.case = self.get_case()
                            child2.mood = self.get_gender()

                            self.verb_form = "Fin"
                            self.orig_lemma = "be"
                            self.lemma = "esse"
                            self.tense = "futureI"
                            self.voice = "active"
                            self.mood = "ind"

                            
                            child2.update(in_handle_aux=True, exclusions=["orig_lemma", "lemma", "verb_form", "tense", "voice", "mood", "gender"])
                            self.update(in_handle_aux=True, exclusions=["verb_form", "orig_lemma", "lemma", "tense", "voice", "mood"])
                            child1.ignore()
                            child3.ignore()
                            break


    def get_latmor(self):
        if self.verb_form == "Fin":
            # cantabo --> cantare<V><futureI><ind><active><sg><1>
            return "%s<%s><%s><%s><%s><%s><%d>" % (self.inf, VERBlm, self.tense, self.mood, self.voice, self.number, self.person)

        if self.verb_form == "Part":
            if not self.gender:
                self.gender = "masc"

            # delectans --> delectare<V><part><pres><active><masc><sg><acc>
            return "%s<%s><part><%s><%s><%s><%s><%s>" % (self.inf, VERBlm, self.tense, self.voice, self.gender, self.number, self.case) 

        if self.verb_form == "Inf":
            # delectare --> delectare<V><pres><inf><active>
            return "%s<%s><%s><inf><%s>" % (self.inf, VERBlm, self.tense, self.voice)

        if self.verb_form == "gerundivum":
            # delectandus --> delectare<V><gerundivum><positive><masc><sg><nom>
            return "%s<%s><positive><%s><%s><%s>" % (self.inf, self.verb_form, self.gender, self.number, self.case)


        return "INVALID_VERB_FORM"


class Indecl(Word):
    def __init__(self, wordinfo):
        Word.__init__(self, wordinfo)

        self.pos = self.get_pos()
        self.latmor = self.get_latmor()

    def get_pos(self):
        if self.isord(): return NUM
        if self.pos == ADP: return PREP
        if self.pos in (CCONJ, SCONJ): return CONJ
        if self.pos in (INTJ, NUM, PART): return self.pos
        return self.pos

    def get_latmor(self):
        return "%s<%s>" % (self.lemma, self.pos)

def makeword(wordinfo):
    index, form, lemma, pos, feats_str, parent, deprel, orig_lemma = wordinfo
    lemma_lower = lemma.lower()

    if lemma_lower == "amen": 
            word = Word(wordinfo)
            word.latmor = "IRREG_āmēn" if lemma == lemma_lower else "IRREG_Āmēn"
    elif lemma_lower in ["quot", "quotquot"]:
        word = Word(wordinfo)
        word.latmor = "IRREG_"+lemma
    elif lemma_lower in ["iesus", "iesum", "iesu"]:
        word = Noun(wordinfo)
        if "Case=Nom" in feats_str: word.latmor = "IRREG_" + lemma[0] + "ēsus"
        elif "Case=Acc" in feats_str: word.latmor = "IRREG_" + lemma[0] + "ēsum"
        else: word.latmor = "IRREG_" + lemma[0] + "ēsū"

    #
    # elif lemma.endswith("que") or lemma.endswith("ve") or lemma.endswith("ne"):
    #     particle = lemma[-3:] if lemma.endswith("que") else lemma[-2:]
    #     mainlemma = lemma[:-3] if lemma.endswith("que") else lemma[:-2]
    #     word = makeword(wordinfo, nodes, node_id)
    #     word.latmor += " %s<PART>" % particle
    #

    # Normal cases
    elif pos == "PUNCT":
        word = Word(wordinfo)
        word.latmor = "PUNCT_" + lemma
    elif pos in ("NOUN", "PROPN", "PRON"):
        word = Noun(wordinfo)
        #print word.feats_str, word.feats
    elif pos in ("ADJ", "DET", "NUM"):
        word = Adj(wordinfo)
    elif pos == "ADV":
        word = Adv(wordinfo)
    elif pos in ["VERB", "AUX"]:
        word = Verb(wordinfo)
        
        #if "VerbForm=Fin" in feats_str:     word = VerbFin(wordinfo)
        #elif "VerbForm=Inf" in feats_str:   word = VerbInf(wordinfo)
        #elif "VerbForm=Part" in feats_str:  word = VerbPart(wordinfo)
        #else:                               word = VerbFin(wordinfo)

    # Default case
    else:
        word = Indecl(wordinfo)

    return word