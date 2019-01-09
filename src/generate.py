# -*- coding: utf-8 -*-

import words, structure
import sys, os
import multiprocessing as mp

def make_latmors(filenum, root, nodes):
    structure.print_tree(root)

    latmor_filename = "./latmor_files/latmor"+filenum+".txt"
    latmors = [node.word.latmor for (index, node) in nodes.iteritems()]
    with open(latmor_filename, "w") as latmor_file:
        for lm in latmors: latmor_file.write(str(lm) + '\n')


def generate(parse_filename):
    filenum = structure.get_parsefilenum(parse_filename)
    source_rawparse, target_rawparse = structure.read_parsefiles(parse_filename)
    
    latmor_filename = "./latmor_files/latmor"+filenum+".txt"

    wordinfos = structure.get_all_wordinfos_from_parse(parse_filename)
    root, nodes = structure.maketree(parse_filename, wordinfos=wordinfos)
    ignore_indices = [i for i, node in nodes.iteritems() if node.word.is_ignored()]
    
    make_latmors(filenum, root, nodes)



    
    sys.stderr.write("BATCH GENERATION:\n")
    with os.popen("fst-infl LatMor/latmor-gen.a < "+latmor_filename) as latmor_gen_process_out:
        latmor_gens = [lg.strip() for lg in latmor_gen_process_out]

    #with open(latmor_filename, "r") as f:
    #    for line in f: print line.strip()

    latmor_gens_temp = list()
    j = -1
    for i in range(len(latmor_gens)):
        lg = latmor_gens[i]
        if latmor_gens[i].startswith(">"):
            j += 1
            latmor_gens_temp.append(list())
            continue

        latmor_gens_temp[j].append(latmor_gens[i])

    latmor_gens = [sorted(lg_list)[0] for lg_list in latmor_gens_temp]
    latmor_gens = dict([(i+1, latmor_gens[i]) for i in range(len(latmor_gens))])
    
    for key in latmor_gens.keys():
        if latmor_gens[key].startswith("no result for"):
            latmor_gens[key] = latmor_gens[key].replace("no result for", "").strip()

            if latmor_gens[key].startswith("PUNCT_") or latmor_gens[key].startswith("IRREG_"):
                latmor_gens[key] = latmor_gens[key][6:]

            elif not latmor_gens[key].startswith("*"):
                latmor_gens[key] = "*" + latmor_gens[key]

        else:
            latmors = words.Word.get_all_latmors(latmor_gens[key], form_macronized=True)

            for lm in latmors:
                if "<alt>" in lm:
                    lm = lm.replace("<alt>", "")
                    latmor_gens[key] = words.Word.get_indiv_gen(lm, resolve_alt=True)
                    break

    print "PRE-IGNORE"
    for i, lg in latmor_gens.iteritems(): print i, lg

    for i in ignore_indices:
        del nodes[i]
        del latmor_gens[i]

    print "COMPARISON:"
    for i in nodes:
        print nodes[i].word.latmor, latmor_gens[i]



    print "\nPOST-IGNORE"
    for i, lg in latmor_gens.iteritems(): print i, lg



    replacements = dict()
    for i in latmor_gens:
        if not latmor_gens[i].startswith("*"): continue

        wordinfo = wordinfos[i]
        index, form, lemma, pos, feats_str, parent_index, deprel, orig_lemma = wordinfo

        node = nodes[i]
        word = node.word
        latmor = word.latmor
        gen = word.__class__.get_indiv_gen(latmor, word=word)
        if '*' not in gen:
            replacements[i] = gen
            continue

        new_word = words.Indecl(wordinfo)
        new_word.parent = word.parent
        new_word.children = word.children
        new_word.siblings = word.siblings
        new_word.update()
        node.word = new_word
        new_latmor = new_word.latmor
        new_gen = new_word.__class__.get_indiv_gen(new_latmor, word=new_word)
        if '*' not in new_gen:
            replacements[i] = new_gen
            continue

        node.word = word
        default_latmor = words.Word.get_latmor_default(word.lemma)
        default_gen = words.Word.get_indiv_gen(default_latmor, word=word)
        if '*' not in default_gen:
            replacements[i] = default_gen


    for k, v in replacements.iteritems():
        latmor_gens[k] = v

    
    filename = "gen"+filenum+".txt"
    with open("./gen/"+filename, "w") as f:
        output_line = ' '.join(latmor_gens.values()).strip() + '\n\n'
        f.write(output_line)

#####################################


parse_files = sorted([filename for filename in os.listdir("./parses/target") if filename.endswith(".conllu")])
print "PARSE_FILES"
for pf in parse_files: print pf


if len(sys.argv) > 1:
    filenum = int(sys.argv[1])
    generate(parse_files[filenum])    
else:
    #for pf in parse_files: generate(pf)
    
    p = mp.Pool(processes=8)
    p.map(generate, parse_files)
    p.close()
    
