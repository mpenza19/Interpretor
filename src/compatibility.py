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
