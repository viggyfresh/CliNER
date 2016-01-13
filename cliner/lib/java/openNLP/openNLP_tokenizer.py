
"""
    This was not used. I was trying out different
    tokenization methods.
"""

from subprocess import Popen, PIPE, STDOUT

from py4j.java_collections import JavaArray
from py4j.java_gateway import JavaGateway

import re
import os
import time
import sys

gateway_dir = os.environ["CLINER_DIR"] + "/clicon/lib/java/entry_point"

"""
    for whatever reason py4j does not run unless the directory is changed
    to the gateway dir or a network error is thrown.
"""
#os.chdir(gateway_dir)

sys.path.append(gateway_dir)

from gateway import GateWayServer

class OpenNLPTokenizer:

    def __init__(self):

        print "calling constructor"

        # launches java gateway server.
        self.gateway_server = GateWayServer()

        self.gateway = JavaGateway()

        # limit how long to wait for connection to gateway to be available.
        kill_time = 20
        init_time = time.time()

        while True:

            if time.time() - init_time > kill_time:
                exit("\ncould not establish connection to gateway...")

            try:
                self.tokenizer = self.gateway.entry_point.getOpenNlpTokenizer()
                break
            except:
                continue

    def __del__(self):

        self.gateway.detach(self.tokenizer)
        self.gateway.close()

        self.tokenizer = None
        self.gateway = None

    def preProcess(self, text):
        """ sentenizes and then tokenizes text """
        ret_val = []
        for tokenized_sent in self.tokenizer.preProcess(text):
            tmp = []
            for token in tokenized_sent:
                tmp.append(token)
            ret_val.append(tmp)

        return ret_val

    def sentenize(self, text):

        sentences = []

        for sent in self.tokenizer.sentenize(text):
            sentences.append(sent)

        return sentences

    def tokenize(self, string):

        tokens = []

        for tok in self.tokenizer.tokenize(string):
            tokens.append(tok)

        return tokens

if __name__ == "__main__":

    t = OpenNLPTokenizer()
    print t.preProcess("hello world! this is a test sentence. i hope this becomes a seperate sentence.")
    print t.sentenize("hello world. this is a test sentence")
    print t.tokenize("hello world!")


# EOF

