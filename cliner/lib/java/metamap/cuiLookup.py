
from subprocess import check_output
from py4j.java_gateway import JavaGateway, Py4JNetworkError

from metamap_server_launcher import MetaMapServer

import time
import sys
import os
import re

if "CLINER_DIR" not in os.environ:
    exit("CLINER_DIR not defined")

gateway_dir = os.environ["CLINER_DIR"] + "/cliner/lib/java/entry_point"

sys.path.append(gateway_dir)

from gateway import GateWayServer

from socket import error

class MetaMap(object):

    def __init__(self):

        MetaMapServer.start_server()
        # launches java gateway server.
        GateWayServer.launch_gateway()

        init_time = time.time()

        while True:

            try:

                self.gateway = JavaGateway(eager_load=True)
                self.metamap = self.gateway.entry_point.getMetaMapObj()

            except:

                if (time.time() - init_time) > 60:
                    exit("Could not load necessary dependencies...")
                else:
                    time.sleep(5)
                    continue

            break


    def getConceptIds(self, phrase):
        """
        performs a cui lookup on a phrase using metamap java api.
        """

        phrase = re.sub("\n", "", phrase)

        retVal = []

        output = self.metamap.getCuis(phrase)

        results = output.split('\n')[:-1]

        results = [line.split('&&') for line in results]

        if len(results) != 1:

            print len(results)

            print "phrase: ", phrase
            print "results: ", results

            exit("error")

        for candidates in results:

            mappings = {}

            norm_phrases = set()

            for candidate in candidates:

                candidate = candidate.split('|')

                norm = candidate[1]
                name = candidate[3]
                cui  = candidate[5]

                norm_phrases.add(norm)

                if name in mappings:
                    mappings[name].add(cui)
                else:
                    mappings[name] = set([cui])

            retVal.append({"norms":norm_phrases, "text":phrase, "mappings":mappings})

        assert(len(retVal) == 1)

        return retVal

if __name__ == "__main__":

    # launches java gateway server.
    m = MetaMap()

    phrases = ["Dribbling from mouth",
               "Bleeding from nose",
               "Hemorrhage from mouth",
               "Chest pain at rest",
               "Fatigue during pregnancy"]

    phrases = ["a second glucagon shot"]

    for phrase in phrases[0:1]:
        print phrase
        print
        print m.getConceptIds(phrase)


# EOF

