# -*- coding: utf-8 -*-

import sys, traceback, os
import multiwordnet.db as db
from multiwordnet.wordnet import WordNet
import Levenshtein 

libdir = "/usr/local/lib/python3.6/site-packages/multiwordnet/db/"

eng_numbers = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
lat_numbers = ("unus", "duo", "tres", "quattuor", "quinque", "sex", "septem", "octo", "novem", "decem")

def conditional_compile(language):
    db_files = list()
    sql_files = list()
    for f in os.listdir(libdir + language):
        if f.endswith(".sql"): sql_files.append(f)
        elif f.endswith(".db"): db_files.append(f)
    
    if len(db_files) != len(sql_files): 
        db.compile(language)


class LemmaTrans:
    def __init__(self, direction):
        conditional_compile("english")
        conditional_compile("latin")
        self.dir = direction
        self.source_wn, self.target_wn = self.instantiate_wordnets()

    def instantiate_wordnets(self):
        if self.dir == "eng2lat":
            swn = WordNet('english')
            twn = WordNet('latin')
        elif self.dir == "lat2eng":
            swn = WordNet('latin')
            twn = WordNet('english')
        else:
            sys.stderr.write("Invalid input: direction (sys.argv[1]) must be 'eng2lat' or 'lat2eng'.\n")
            exit()

        return swn, twn

    def get_best_target_synset(self, source_synsets, source_lemma):
        try:
            sorted_source_synsets = list()
            for s in source_synsets:
                try: lemmas = s.lemmas
                except: continue

                remove_indices = list()
                for i in range(len(lemmas)):
                    l = lemmas[i]
                    if not l: remove_indices.append(i)

                for i in reversed(remove_indices):
                    lemmas.pop(i)

                do_append = True

                for l in lemmas:
                    if not l: continue
                    if "_" in l.lemma or "'" in l.lemma:
                        do_append = False

                if do_append: sorted_source_synsets.append(s)

            sorted_source_synsets = sorted(sorted_source_synsets, key=lambda s: len(s.lemmas))
            source_synsets = sorted_source_synsets
            #print("OK")

        except:
            self.handle_err(source_lemma)

        max_len_source = 0
        max_len_target = 0
        for source_ss in source_synsets:
            source_ss_len = source_ss.lemma_count
            if source_ss_len > max_len_source: max_len_source = source_ss_len
            
            target_ss = self.target_wn.get_synset(source_ss.id)
            target_ss_len = target_ss.lemma_count
            if target_ss_len > max_len_target: max_len_target = target_ss_len

        max_score = 0
        max_score_index = 0

        rankings = dict()
        for i in range(len(source_synsets)):
            source_ss = source_synsets[i]
            source_ss_len = source_ss.lemma_count

            target_ss = self.target_wn.get_synset(source_ss.id)
            target_ss_len = target_ss.lemma_count

            for j in range(len(source_ss.lemmas)):
                l = source_ss.lemmas[j]
                if l and l == source_lemma:
                    index_lemma_in_source_ss = j
            else: index_lemma_in_source_ss = -1 

            this_score = max_len_source - source_ss_len - index_lemma_in_source_ss - target_ss_len            

            if this_score > max_score:
                max_score = this_score
                max_score_index = i
            
            rankings[i] = this_score

        rankings = sorted(rankings.items(), key=lambda kv: kv[1], reverse=True)
        ranked_synsets = [source_synsets[index] for (index, score) in rankings if self.target_wn.get_synset(source_synsets[index].id).lemma_count > 0]
        
        best_source_synset = ranked_synsets[0] if len(ranked_synsets) > 0 else None
        best_target_synset = self.target_wn.get_synset(best_source_synset.id) if best_source_synset else None

        return best_target_synset

    def get_best_target_lemma(self, source_lemma, target_synset):    
        source_rawlemma = source_lemma.lemma

        max_similarity = 0
        max_similarity_index = 0

        lemmas = [l for l in target_synset.lemmas if l and "_" not in l.lemma] if target_synset else list()
        

        if len(lemmas) == 0: return

        for i in range(len(lemmas)):
            l = lemmas[i]
            this_rawlemma = l.lemma
            similarity = Levenshtein.ratio(source_rawlemma, this_rawlemma)
            if similarity > max_similarity:
                max_similarity = similarity
                max_similarity_index = i
        
        return lemmas[max_similarity_index]

    def translate_lemma(self, source_rawlemma, pos):
        #print("source raw lemma:", source_rawlemma)        

        irreg = self.handle_irreg(source_rawlemma, pos)
        if irreg:
            #print("irreg")
            #print("target raw lemma:", irreg)
            return irreg

        if source_rawlemma not in ("I", "God"): source_rawlemma = source_rawlemma.lower()

        irreg = self.handle_irreg(source_rawlemma, pos)
        if irreg:
            #print("irreg")
            #print("target raw lemma:", irreg)
            return irreg
        
       #print("not irreg")

        try:
            source_lemma = self.source_wn.get_lemma(source_rawlemma, pos)
        except:
            return self.handle_err(source_rawlemma)

        if not source_lemma:
            return self.handle_err(source_rawlemma)
        
        #print("source lemma found")

        source_synsets = source_lemma.synsets
        #print("source synsets found")
        
        target_synset = self.get_best_target_synset(source_synsets, source_lemma)
        #print("target synsets found")

        target_lemma = self.get_best_target_lemma(source_lemma, target_synset)
        if target_lemma:
            target_rawlemma = target_lemma.lemma
            #print("target lemma found")
        else:
            target_rawlemma = self.handle_err(source_rawlemma)
        
        #print("target raw lemma:", target_rawlemma)
        return str(target_rawlemma)

    def handle_irreg(self, source_rawlemma, pos):
        if pos in ("u", "intj"): return source_rawlemma
        
        elif self.source_wn.language == "english" and self.target_wn.language == "latin":
            if source_rawlemma in eng_numbers:
                #print(source_rawlemma)
                #print("NUMBER HERE:", source_rawlemma, lat_numbers[eng_numbers.index(source_rawlemma)])
                return lat_numbers[eng_numbers.index(source_rawlemma)]

            if source_rawlemma == "Jesus" and pos == "n": return "Iesus"
            if source_rawlemma in ("Lord", "master", "lord"): return "dominus"
            if source_rawlemma.lower() in ("holy", "saint", "saintly", "sainted"): return "sanctus"
            if source_rawlemma == "sacred" and pos == "a": return "sacer"
            if source_rawlemma == "the" and pos == "a": return "ille"
            if source_rawlemma == "a" and pos == "a": return "unus"
            if source_rawlemma == "not": return "non"
            if source_rawlemma == "no" and pos == "a": return "nullus"
            if source_rawlemma in ("from", "out") and pos == "s": return "ex"
            if source_rawlemma == "of": return "de"
            if source_rawlemma == "about" and pos == "s": return "de"
            if source_rawlemma == "about" and pos == "r": return "mox"
            if source_rawlemma == "by" and pos == "s": return "ab"
            if source_rawlemma == "be" and pos == "v": return "sum"
            if source_rawlemma == "word" and pos == "n": return "verbum"
            if source_rawlemma in ("in", "into", "upon", "at") and pos == "s": return "in"
            if source_rawlemma == "on" and pos == "s": return "super"
            if source_rawlemma == "and": return "et"
            if source_rawlemma == "or": return "vel"
            if source_rawlemma == "nor": return "nec"
            if source_rawlemma == "neither": return "neque"
            if source_rawlemma == "but": return "sed"
            if source_rawlemma == "yet" and pos == "c": return "at"
            if source_rawlemma == "with": return "cum"
            if source_rawlemma == "without": return "sine"
            if source_rawlemma == "that" and pos == "c": return "ut"
            if source_rawlemma == "God": return "Deus"
            if source_rawlemma in ("this", "these") and pos in ("p", "a"): return "hic"
            if source_rawlemma == "those" and pos in ("p", "a"): return "ille"
            if source_rawlemma in "that" and pos == "a": return "ille"
            if source_rawlemma == "that" and pos == "p": return "qui"
            if source_rawlemma in ("who", "whom", "whose", "which", "what"): return "qui"
            if source_rawlemma in ("I", "myself", "we", "me", "us") and pos == "p": return "ego"
            if source_rawlemma in ("my", "mine") and pos in ("a", "p"): return "meus"
            if source_rawlemma in ("our", "ours") and pos in ("a", "p"): return "noster"
            if source_rawlemma in ("you", "yourself"): return "tu"
            if source_rawlemma in ("your", "yours") and pos in ("a", "p"): return "tuus"
            if source_rawlemma in ("he", "him", "himself", "she", "her", "herself", "it", "itself", "they", "them", "themselves") and pos == "p": return "is"
            if source_rawlemma in ("his", "her", "hers", "their", "theirs") and pos in ("a", "p"): return "is"
            if source_rawlemma == "own" and pos == "a": return "suus"
            if source_rawlemma in ("all", "every") and pos in ("a", "p"): return "omnis"
            if source_rawlemma.startswith("any") or source_rawlemma in ("other", "another"): return "alius"
            if source_rawlemma in ("toward", "towards"): return "ad"
            if source_rawlemma == "to" and pos == "s": return "ad"
            if source_rawlemma == "through": return "per"
            if source_rawlemma == "before": return "ante"
            if source_rawlemma == "after": return "post"
            if source_rawlemma == "around": return "circum"
            if source_rawlemma == "against": return "contra"
            if source_rawlemma == "between": return "inter"
            if source_rawlemma == "among": return "apud"
            if source_rawlemma == "within": return "intra"
            if source_rawlemma == "outside": return "extra"
            if source_rawlemma == "beyond": return "ultra"
            if source_rawlemma == "across": return "trans"
            if source_rawlemma == "above": return "super"
            if source_rawlemma == "over" and pos == "s": return "super"
            if source_rawlemma in ("below", "under"): return "sub"        
            if source_rawlemma == "then": return "deinde"
            if source_rawlemma in ("for", "because") and pos == "c": return "quoniam"    
            if source_rawlemma == "for" and pos == "s": return "pro"
            if source_rawlemma in ("also", "too"): return "quoque"
            if source_rawlemma in ("near", "nearby", "nearly") and pos in ("r", "s"): return prope
            if source_rawlemma == "almost": return "quasi"
            if source_rawlemma in ("alone", "only", "sole") and pos == "a": return "solus"
            if source_rawlemma in ("alone", "only", "solely") and pos == "r": return "solum"
            if source_rawlemma in ("like", "as") and pos == "c": return "sicut"
            if source_rawlemma == "like" and pos == "r": return "sicut"
            if source_rawlemma in ("like", "as"): return "ut"
            if source_rawlemma in ("while", "meanwhile") and pos == "r": return "dum"
            if source_rawlemma == "unti": return "donec"
            if source_rawlemma == "fulness" and pos == "n": return "plenitudo"
            if source_rawlemma == "ever" and pos == "r": return "umquam"
            if source_rawlemma == "never" and pos == "r": return "numquam"
            if source_rawlemma == "when": return "quando"
            if source_rawlemma == "John": return "Ioannes"
            if source_rawlemma == "answer" and pos == "v": return "respondeo"
            if source_rawlemma in ("say", "tell") and pos == "v": return "dico"
            if source_rawlemma == "next" and pos == "a": return "proximus"
            if source_rawlemma == "previous" and pos == "a": return "prior"    
            if source_rawlemma == "where" and pos == "c": return "ubi"
            if source_rawlemma == "there" and pos == "c": return "ibi"
            if source_rawlemma == "how" and pos in ("r", "c"): return "quomodo"
            if source_rawlemma == "than" and pos == "s": return "quam"
            if source_rawlemma in ("Mary", "Maria"): return "Maria"
            if source_rawlemma == "Joseph": return "Iosephus"
            if source_rawlemma == "have" and pos == "v": return "habeo"
            if source_rawlemma in ("although", "though"): return "quamquam"
            if source_rawlemma == "however": return "tamen"
            if source_rawlemma == "both": return "ambo"
            if source_rawlemma in ("great", "greater", "greatest"): return "magnus"
            if source_rawlemma in ("can", "could"): return "possum"
            
        
        elif self.source_wn.language == "latin" and self.target_wn.language == "english":
            if source_rawlemma == "sum" and pos == "v": return "be"
            if source_rawlemma == "verbum" and pos == "n": return "word"
            if source_rawlemma == "in" and pos == "s": return "in"
            if source_rawlemma in ("et", "ac", "atque", "que"): return "and"
            if source_rawlemma in ("vel", "aut", "ve"): return "or"
            if source_rawlemma in ("cum", "apud") and pos == "s": return "with"
            if source_rawlemma == "cum" and pos == "c": return "when"
            if source_rawlemma == "deus" and pos == "n": return "god"
            if source_rawlemma == "Deus" and pos == "n": return "God"
            if source_rawlemma == "hic" and pos in ("p", "a"): return "this"
            if source_rawlemma in lat_numbers: return eng_numbers[lat_numbers.index(source_rawlemma)]

        else:
            sys.stderr.write("ERROR: Invalid translation direction. Must be 'eng2lat' or 'lat2eng'.\n")
            exit()

    def handle_err(self, source_rawlemma):
        sys.stderr.write("ERROR: Lexicon cannot find translation for source lemma '%s'\n" % source_rawlemma)
        sys.stderr.flush()
        target_rawlemma = "*%s" % source_rawlemma
        #sys.stderr.write("target raw lemma: " + target_rawlemma + '\n')
        return target_rawlemma

def translate_sentence(direction, source_sentence, source_pos):
    lt = LemmaTrans(direction)

    target_sentence = list()
    for w in range(len(source_sentence)):
        source_rawlemma = source_sentence[w]
        pos = source_pos[w]

        try:
            target_rawlemma = lt.translate_lemma(source_rawlemma, pos)

        except:
            target_rawlemma = lt.handle_err(source_rawlemma)

        if not target_rawlemma:
            target_rawlemma = lt.handle_err(source_rawlemma)
        
        target_sentence.append(target_rawlemma)
    
    return target_sentence

def test_word(lt):

    if len(sys.argv) < 4:
        sys.stderr.write("ERROR: To test-translate a single word, must provide lemma and POS as command-line args.\n")
        return
    

    source_rawlemma, pos = sys.argv[2], sys.argv[3]

    print("SINGLE-WORD TRANSLATION")
    target_rawlemma = lt.translate_lemma(source_rawlemma, pos)
    print(source_rawlemma, '-->', target_rawlemma)
    

if len(sys.argv) > 1:
    LT = LemmaTrans(sys.argv[1])
    test_word(LT)