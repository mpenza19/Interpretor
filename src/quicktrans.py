lexicon = dict()
lexicon["girl"] = "puella"
lexicon["tree"] = "arbor"
lexicon["under"] = "sub"
lexicon["sit"] = "sedeo"
lexicon["the"] = ""
lexicon["a"] = ""

def lemmatize(token):
    if token.startswith("girl"): return "girl"
    if token.startswith("tree"): return "tree"
    if token.startswith("sit"): return "sit"

    if token.startswith("puell"): return "puella"
    if token.startswith("arbor"): return "arbor"
    if token.startswith("sede"): return "sedeo"

    return token
    

eng = "the girl sits under a tree"
lat = "puella sub arbore sedet"

print "ORIGINAL ENGLISH:", eng
print "ORIGINAL LATIN:", lat

lem_eng = ""
lem_lat = ""

for word in eng.split():
    lem_eng += lemmatize(word) + " "
lem_eng = lem_eng.strip()

for word in lat.split():
    lem_lat += lemmatize(word) + " "
lem_lat = lem_lat.strip()

print "LEMMATIZED ENGLISH:", lem_eng
print "LEMMATIZED LATIN:", lem_lat

trans_lat = ""
trans_eng = ""

for word in lem_eng.split():
    trans_lat = (trans_lat + lexicon[word]).strip() + " "
trans_lat = trans_lat.strip()


print "ENGLISH TO LATIN:", trans_lat
# print "LATIN TO ENGLISH:", trans_eng
