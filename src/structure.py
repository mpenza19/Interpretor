# -*- coding: utf-8 -*-

from anytree import Node, RenderTree, LevelOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph
import words
import sys


def get_parsefilenum(parse_filename):
    return parse_filename[6:parse_filename.find(".")].zfill(4)

def read_parsefiles(parse_filename):
    with open("./parses/source/"+parse_filename, "r") as f:
        source_rawparse = [line.split('\t') for line in f]
        source_rawparse = [line for line in source_rawparse if line != ['\n'] and not line[0].startswith("#")]

    with open("./parses/target/"+parse_filename, "r") as f:
        target_rawparse = [line.split('\t') for line in f]
        target_rawparse = [line for line in target_rawparse if line != ['\n'] and not line[0].startswith("#")]

    return source_rawparse, target_rawparse


def get_wordinfo_from_parse(source_line, target_line):
    index = int(target_line[0])
    form = ""
    lemma = target_line[2] if "#" not in target_line[2] else target_line[2][:target_line[2].find("#")]   
    pos = target_line[3]
    feats_str = target_line[5]
    parent = int(target_line[6])
    deprel = target_line[7]
    orig_lemma = source_line[2]
    orig_lemma = orig_lemma.lower() if orig_lemma not in ("I", "God") and pos != "PROPN" else orig_lemma
    lemma = lemma.lower() if lemma != "Deus" and pos != "PROPN" else lemma
    
    form, lemma, pos, feats_str = irreg_replacements(form, lemma, pos, feats_str)

    return index, form, lemma, pos, feats_str, parent, deprel, orig_lemma

def irreg_replacements(form, lemma, pos, feats_str):
    # Handle replacements for irregular cases
    if lemma == "sum":
        lemma = "esse"

    elif lemma == "omnis":
        pos = "DET"

        if "Number=Sing" in feats_str:
            feats_str = feats_str.replace("Number=Sing", "Number=Plur")
        else:
            if feats_str in ("", "_"):
                feats_str = "Number=Plur"
            else:
                feats_str += "|Number=Plur"

    elif lemma == "suus":
        pos = "ADJ"
        
        if feats_str in ("", "_"):
            feats_str = "Poss=Yes"
        else:
            feats_str += "|Poss=Yes"
        


    elif lemma in ("Ierosolyma", "Ierusalem", "Hierusalem", "Hierosolymae"):
        lemma = "Hierosolyma"

    elif lemma in ("autem", "neque"):
        pos = "CCONJ"

    elif lemma in ("nihil", "nemo", "aliquis"):
        pos = "PRON"
        feats_str += "|PronType=Ind"

    elif lemma == "ille":
        pos = "PRON"
        feats_str += "|PronType=Dem"

    elif lemma in ("ipse", "is"):
        feats_str = feats_str.replace("PronType=Prs", "PronType=Dem")
        feats_str = feats_str.replace("|Poss=Yes", "")

    elif lemma == "qui" and "PronType=Int" in feats_str:
        feats_str = feats_str.replace("PronType=Int", "PronType=Rel")        

    if lemma == "ipse" and form.lower() == "ipsud":
        form = "ipsum"

    return form, lemma, pos, feats_str

def get_all_wordinfos_from_parse(parse_filename):
    filenum = get_parsefilenum(parse_filename)
    source_rawparse, target_rawparse = read_parsefiles(parse_filename)
    
    # Adapted from ScanLat:parse.py
    wordinfos = dict([(i+1, get_wordinfo_from_parse(source_rawparse[i], target_rawparse[i])) for i in range(len(source_rawparse))])

    return wordinfos


def makenode(wordinfo):
    word = words.makeword(wordinfo)
    node = Node(word.lemma, word=word, prev=None, next=None)
    return node



def buildtree(wordinfos):
    parents = dict([(index, parent) for index, form, lemma, pos, feats_str, parent, deprel, orig_lemma in wordinfos.values()])
    nodes   = dict([(wordinfo[0], makenode(wordinfo)) for wordinfo in wordinfos.values()])
    for i in nodes: nodes[i].word.set_nodes_info(nodes, i)
    
    # Find root
    for i in nodes:
        if parents[i] == 0:
            root = nodes[i]
            break
    else:
        sys.stderr.write("ERROR: NO ROOT\n")
        exit()

    # Set nodes' and words' parent, prev, and next links
    keys = nodes.keys()
    for k in range(len(keys)):
        i = keys[k]
        this_node = nodes[i]

        if parents[i] != 0:
            this_node.parent = nodes[parents[i]]
            this_node.word.parent = this_node.parent.word

        if k > 0:
            i_prev = keys[k-1]
            prev_node = nodes[i_prev]
            this_node.prev = prev_node
            this_node.word.prev = prev_node.word

        if k < len(keys)-1:
            i_next = keys[k+1]
            next_node = nodes[i_next]
            this_node.next = next_node
            this_node.word.next = next_node.word

    # Set words' children and siblings links
    for (i, this_node) in nodes.iteritems():
        this_node.word.children = [child.word for child in this_node.children]
        this_node.word.siblings = [sibling.word for sibling in this_node.siblings]

    for this_node in nodes.values():
        this_node.word.update()
        
    return root, nodes


def maketree(parse_filename, wordinfos=None):
    if not wordinfos: wordinfos = get_all_wordinfos_from_parse(parse_filename)
    root, nodes = buildtree(wordinfos)

    return root, nodes


def print_tree(root):
    # Print tree from root
    for pre, fill, node in RenderTree(root):
        print "%s%s :: %s :: %s" % (pre.encode('utf8'), node.name, node.word.deprel, node.word.orig_lemma)
    print "\n---------\n"

def print_orig_tree(root):
    # Print tree from root
    with open("root.txt", "w") as f:
        for pre, fill, node in RenderTree(root):
            f.write("%s%s :: %s\n" % (pre.encode('utf8'), node.word.orig_lemma, node.word.deprel))


def test_eng_tree():
    parse_filename = "parses0000.conllu"
    root, nodes = maketree(parse_filename)
    print "\n\n"
    print_orig_tree(root)
    print "\n\n"

#test_eng_tree()