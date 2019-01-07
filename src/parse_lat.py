
import sys, os, string
reload(sys)
sys.setdefaultencoding('utf-8')

import clean
from ufal.udpipe import Model, Pipeline, ProcessingError 
from words import Noun, Adj, Adv, Verb, VerbFin, VerbInf, VerbPart, Indecl
import words

def config():
    # In Python2, wrap sys.stdin and sys.stdout to work with unicode.
    if sys.version_info[0] < 3:
        import codecs, locale
        global encoding
        encoding = locale.getpreferredencoding()
        sys.stdin = codecs.getreader(encoding)(sys.stdin)
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)

def get_pipeline():
    # Load model, handle errors
    global model
    sys.stderr.write('Loading model... ')
    model_filename = "../UDPipe-ud2-3/latin-proiel-ud-2.3.udpipe"
    model = Model.load(model_filename)
    if not model:
        sys.stderr.write("Cannot load model from file '%s'\n" % model_filename)
        sys.exit(1)
    sys.stderr.write('Done.\n')

    # Create model pipeline
    pipeline = Pipeline(model, "horizontal", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
    error = ProcessingError()

    return pipeline, error

def process_text(txt, pipeline, error):
    # Process input text
    processed = pipeline.process(txt, error)
    
    if error.occurred():
        sys.stderr.write("An error occurred when running run_udpipe: ")
        sys.stderr.write(error.message)
        sys.stderr.write("\n")
        sys.exit(1)

    return processed

def main():
    # Read input text from stdin
    txt = clean.demacronized_lines(sys.stdin.read())

    filenum = 0
    filename = "text/text%i.txt" % filenum
    f = open(filename, "w")
    for line in txt.splitlines():
        f.write(line.strip() + ' ')
        if "." in line or "?" in line or "!" in line:
            f.close()
            filenum += 1
            filename = "text/text%i.txt" % filenum
            f = open(filename, "w")
        
    f.close()


    config()
    pipeline, error = get_pipeline()
    
    textfiles = sorted([filename for filename in os.listdir("./text") if filename.endswith(".txt")])
    for tf in textfiles:
        #print "text/"+tf
        with open("./text/"+tf, "r") as f:
            txt = f.read()
            #print txt
            processed = process_text(txt, pipeline, error)
            rawparse = processed.split('\n')

            for line in rawparse:
                if line in (['\n'], ' ', ''): continue
                if line[0].startswith("#"): continue

                pos1 = line[3]
                break
                
            if pos1 != "PROPN":
                txt = txt[0].lower() + txt[1:] if len(txt) > 1 else txt.lower()
                processed = process_text(txt, pipeline, error)
                rawparse = processed.split('\n')

            filename = "./parses/parses"+tf[4:tf.find(".")]+".txt"
            with open(filename, "w") as udpf:
                for line in rawparse:
                    udpf.write(line + '\n')

main()