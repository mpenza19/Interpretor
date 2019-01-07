# -*- coding: utf-8 -*-
import sys, re
reload(sys)
sys.setdefaultencoding('utf-8')

basic_replacements = {
    '0': '',
    '1': '',
    '2': '',
    '3': '',
    '4': '',
    '5': '',
    '6': '',
    '7': '',
    '8': '',
    '9': '',
    
    'ä': 'a',
    'Ä': 'A',
    'á': 'a',
    'Á': 'A',
    'æ': 'ae',
    'ǽ': 'ae',
    'Æ': 'Ae',
    'Ǽ': 'Ae',

    'ë': 'e',
    'Ë': 'E',
    'é': 'e',
    'É': 'E',

    'ï': 'i',
    'Ï': 'I',
    'í': 'i',
    'Í': 'I',

    'ö': 'o',
    'Ö': 'O',
    'ó': 'o',
    'Ó': 'O',
    'œ': 'oe',
    'Œ': 'Oe',

    'ü': 'u',
    'Ü': 'U',
    'ú': 'u',
    'Ú': 'U',

    'ÿ': 'y',
    'Ÿ': 'Y',
    'ý': 'y',
    'Ý': 'Y',
    
    #'j': 'i',
    #'J': 'I',

    '[': '',
    ']': '',
    '(': '',
    ')': '',
    '\'': '',
    '  ': ' ',

    '\n ': '\n',
    ' \n': '\n',
    '\n\n': '\n'
}

newpunct = {
    ',': ' , ',
    '.': ' . ',
    '?': ' ? ',
    '!': ' ! ',
    ':': ' : ',
    ';': ' ; ',
    '–': ' – ',
    '—': ' — ',
    '-': ' - ',

    
    '"': ' " ',
    '“': ' " ',
    '”': ' " ',
    
    '’': " ' ",
    '‘': " ' ",
    '′': " ' ",
    '`': " ' "
}

macron_replacements = {
    'ā': 'a',
    'ē': 'e',
    'ī': 'i',
    'ō': 'o',
    'ū': 'u',
    'ȳ': 'y', # Unicode code 563
    'ӯ': 'y', # Unicode code 1263
    'Ā': 'A',
    'Ē': 'E',
    'Ī': 'I',
    'Ō': 'O',
    'Ū': 'U',
    'Ȳ': 'Y'
}

def multiple_replace(text, adict):
    """ Adapted from 'Python Cookbook' 2nd Ed.: 1.18. Replacing Multiple Patterns in a Single Pass """
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)

def newline_locs(txt):
    locs = []
    for i in range(len(txt)):
        if txt[i] == '\n': locs.append(i)
    return locs

def clean_text(txt):
    return multiple_replace(txt, basic_replacements).replace('\n', ' \n ')

def clean_lines(txt):
    txt = clean_text(txt)
    text = ""
    for line in txt.split('\n'):
        text += multiple_replace(line.strip(), newpunct) + '\n'

    return text

def demacronized_lines(txt):
    return multiple_replace(clean_lines(txt), macron_replacements)

def main():
    print '#### BEGIN TEXT-CLEANING TESTS ##################################'
    
    with open("../input/aeneid_naturalized.txt", 'r') as f: txt = f.read()
    
    print '#### ORIGINAL TEXT ##############################################'
    print txt
    print '#################################################################\n'

    print '#### BASIC TEXT-CLEANING ########################################'
    cleantxt = clean_text(txt)
    print cleantxt
    print '#################################################################\n'

    print '#### LINEBREAK LOCATIONS ########################################'
    print newline_locs(cleantxt)
    print '#################################################################\n'


    print '#### BASIC TEXT-CLEANING WITH LINE-CLEANING #####################'
    print clean_lines(txt)
    
    print '#### TEXT DEMACRONIZATION #######################################'
    print demacronized_lines(txt)
    print '#################################################################\n'

    print '#### END TEXT-CLEANING TESTS ####################################'

#main()