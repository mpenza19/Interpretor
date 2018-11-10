import copy, sys

with open("DICTPAGE.RAW", "r") as f:
    lines = f.readlines()

def pos(line):
    if line[1] in ("ADV", "PREP", "CONJ"): return line[1]
    if line[2] == "N": return "N"
    if line[3] == "ADJ": return "ADJ"
    if line[4] == "V": return "V"

    sys.stderr.write("POS error:" + line + '\n')
    return None

def lemma(line):
    return line[0] 

def gender(line):
    if pos(line) == "N": return line[4]
    return None


def noun_info(line):
    return lemma(line), pos(line), gender(line)

def adj_info(line):
    return lemma(line), pos(line), g


for line in lines[15:50]:
    linecopy = copy.deepcopy(line).strip()

    line = [l.strip(',') for l in line.strip("#")[:line.index("::")].split()[:-2]]
    line.append(linecopy[linecopy.index("::")+3:])

    if pos(line) == "N": print noun_info(line)
    print lemma(line) + '\t\t' + pos(line) + '\t', line




