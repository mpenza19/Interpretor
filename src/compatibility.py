# -*- coding: utf-8 -*-
 
import execnet

def call_python3(module, func, arg_list):
    # Adapted from https://stackoverflow.com/a/44965570
    gw      = execnet.makegateway("popen//python=python3")
    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (module, func))
    channel.send(arg_list)
    return channel.receive()

"""

source_sentences = list()
source_sentences.append("in beginning be word and word be with God and God be word".split())
source_sentences.append("same be in beginning with God".split())
source_sentences.append("son god be man".split())

source_poses = list()
source_poses.append("s n v n c n v s n c n v n".split())
source_poses.append("a v s n s n".split())
source_poses.append("n n v n".split())

arg_list = [source_sentences, source_poses]

result = call_python3("lemma_trans", "translate_sentences", arg_list) 
for sentence in result:
    print ' '.join(sentence)
"""

#arg_list = ["five", "n"]
#result = call_python3("lemma_trans", "translate_lemma", arg_list) 
#print result
