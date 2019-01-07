# -*- coding: utf-8 -*-

import sys, os, string
from compatibility import call_python3
import multiprocessing as mp

pos_converter = {
        "NOUN": 'n',
        "PROPN": 'n',
        "NUM": 'n',
        "VERB": 'v',
        "AUX": 'v',
        "ADJ": 'a',
        "DET": 'a',
        "ADV": 'r',
        "PRON": 'p',
        "PUNCT": 'u',

        "PREP": 's',
        "ADP": 's',
        "CCONJ": 'c',
        "SCONJ": 'c',
        "PART": 'part',
        "INTJ": 'intj'
    }

def get_mwn_pos_list(parse_pos_list):
    return [pos_converter[pos] if pos in pos_converter else 'n' for pos in parse_pos_list]
     
def write_latparse(engparse_filename):
    filenum = engparse_filename[6:engparse_filename.find(".")].zfill(4)

    with open("./parses/source/"+engparse_filename, "r") as f:
        raw_engparse = [line.split('\t') for line in f]

    direction = "eng2lat"
    eng_lemmas = [line[2] for line in raw_engparse if line != ['\n'] and not line[0].startswith('#')]
    parse_pos_list = [line[3] for line in raw_engparse if line != ['\n'] and not line[0].startswith('#')]
    mwn_pos_list = get_mwn_pos_list(parse_pos_list)
    
    arg_list = [direction, eng_lemmas, mwn_pos_list]
    lat_lemmas = call_python3("lemma_trans", "translate_sentence", arg_list)
    print ' '.join(lat_lemmas), '\n'

    with open("./parses/target/"+engparse_filename[:6]+filenum+".txt", "w") as f:
        lemma_index = 0
        for line in raw_engparse:
            if line == ['\n'] or line[0].startswith("#"):
                f.write('\t'.join(line))
                continue

            line[1] = ''
            line[2] = lat_lemmas[lemma_index]
            lemma_index += 1
            f.write('\t'.join(line))


engparse_files = sorted([filename for filename in os.listdir("./parses/source") if filename.endswith(".txt")])


if len(sys.argv) > 1:
    filenum = sys.argv[1].zfill(4)
    engparse_filename = "parses"+filenum+".txt"
    write_latparse(engparse_filename)
else:
    p = mp.Pool(processes=8)
    p.map(write_latparse, engparse_files)
    p.close()
    
    #for epf in engparse_files: write_latparse(epf)