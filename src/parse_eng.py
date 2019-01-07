
import sys, os, string
reload(sys)
sys.setdefaultencoding('utf-8')

import clean
from ufal.udpipe import Model, Pipeline, ProcessingError 

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
    model_filename = "./UDPipe-ud2-3/english-gum-ud-2.3.udpipe"
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

def write_text_files(input_text):
    text = clean.demacronized_lines(input_text)

    filenum = str(0).zfill(4)
    filename = "text/text%s.txt" % filenum
    f = open(filename, "w")
    split_text = text.split()
    i = 0
    while i < len(split_text):
        wordblock = split_text[i]
        wordblock_next = split_text[i+1] if i+1 < len(split_text) else None
        f.write(wordblock.strip() + ' ')
        if wordblock in ".?!":
            if wordblock_next and wordblock_next in "'\"":
                f.write(wordblock_next.strip() + ' ')
                i += 1
                
            f.close()
            filenum = str(int(filenum) + 1).zfill(4)
            filename = "text/text%s.txt" % filenum
            f = open(filename, "w")
        
        i += 1
    f.close()


def main():
    # Read input text from stdin and write it to files sentence-wise
    write_text_files(sys.stdin.read())

    config()
    pipeline, error = get_pipeline()
    
    for tf in sorted([filename for filename in os.listdir("./text") if filename.endswith(".txt")])[:-1]:
        with open("./text/"+tf, "r") as f: txt = f.read()
        processed = process_text(txt, pipeline, error)
        rawparse = processed.split('\n')
        filename = "./parses/source/parses"+tf[4:tf.find(".")]+".txt"
        with open(filename, "w") as udpf:
            for line in rawparse: udpf.write(line + '\n')

main()