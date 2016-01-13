
from subprocess import Popen, PIPE, STDOUT

from py4j.java_collections import JavaArray
from py4j.java_gateway import JavaGateway

import re
import os
import time
import sys

# path of stanford corenlp dir
dependency_dir = os.environ["CLINER_DIR"] + "/cliner/lib/java/stanford_nlp"
gateway_dir = os.environ["CLINER_DIR"] + "/cliner/lib/java/entry_point"

sys.path.append(gateway_dir)

from gateway import GateWayServer

class DependencyParser:

    def __init__(self):

#        print "\nLoading stanford dependency parser..."

        # launches java gateway server.
        GateWayServer.launch_gateway()

        init_time = time.time()

        while True:

            try:

                self.gateway = JavaGateway(eager_load=True)
                self.parser = self.gateway.entry_point.getStanfordParserObj()

            except:

                if (time.time() - init_time) > 60:
                    exit("Could not load dependencies...")
                else:
                    time.sleep(5)
                    continue

            break



    def getNounPhraseHeads(self, string):

        heads = []

        string =  string.lower()

        for head in self.parser.getNounPhraseHeads(string):
            heads.append(head)

        return heads

    def getSentenceStructure(self, string):
        return self.parser.getSentenceStructure(string)

    def _parse_string(self, string):
        return self.parser.getDependencyTree(string)

    def _get_output_field(self, line, field):
        """
        select string fields to obtain from the lines of the parser output

        example input to parser:
            "This is a test sentence."

        NOTE: base 1 indexing for tokens
              the root token has an index of 0

        example line:
            ['1', 'This', '_', 'null', 'null', '_', '5', 'nsubj', '_', '_']
        """

        ret_val = None

        fields = ['_source_index',   # the index of the token in the sentence
                  '_source_token',   # the token at the specified index in the sentence
                  '_target_index',   # the index of the token in which the current token has a relation with
                  '_rel_type']       # the type of relation between the source token and target token

        _source_index = 0
        _source_token = 1
        _target_index = 6
        _rel_type = 7

        if field in fields:
            ret_val = line[eval(field)]

        return ret_val

    def _get_source_index(self, line):
        """ get the source index specified in a line from the output parser """

        return int(self._get_output_field(line, '_source_index'))

    def _get_source_token(self, line):
        """ get the token at the source index specified in a line from the output parser. """

        return str(self._get_output_field(line, '_source_token'))

    def _get_target_index(self, line):
        """ get the target index specified in a line from the output parser """

        return int(self._get_output_field(line, '_target_index'))

    def _get_rel_type(self, line):
        """ get the relation type between two tokens in a line from the output parser """

        return str(self._get_output_field(line, '_rel_type'))

    def _process_parser_output(self, output_from_parser):

        # sentizer and tokenize output from dependency parser
        output_from_parser = [line.split('\t') for line in output_from_parser.split('\n') if line != '']

        # a list of list of lists
        # [ [  [ lines of outut for a sentence, ...  ], ...  ], ...  ]
        return output_from_parser

    def get_collapsed_dependencies(self, string):

        output_from_parser = self._parse_string(string)

        print output_from_parser

        sentence = self._process_parser_output(output_from_parser)

        dependency_group = {}

        for line in sentence:

            if self._get_rel_type(line) == 'erased':
                continue

            dependency_group[self._get_source_index(line)] = {"source_token":self._get_source_token(line),
                                                              "target_index":self._get_target_index(line),
                                                              "rel_type":self._get_rel_type(line)}

        return dependency_group

    def follow_dependency_path(self, token1, token2, dependency_group):

        """
        note: I am assuming token1 and token2 are different since
        semeval is disjoint spans

        TODO: not sure if there are ways for multiple paths to occur.
        """

        start_points = []

        token1_count = 0
        token2_count = 0

        for index in dependency_group:
            if dependency_group[index]["source_token"] == token1:
                start_points.append(dependency_group[index])
                token1_count += 1
            if dependency_group[index]["source_token"] == token2:
                start_points.append(dependency_group[index])
                token2_count += 1

        if token1_count == 0 or token2_count == 0:
            # no possible path between tokens.
            return []

        paths = []

        for start_point in start_points:

            end_token = token2 if start_point["source_token"] == token1 else token1

            path = []

            entry = start_point

            while True:

                path.append(entry["source_token"])
                path.append(entry["rel_type"])

                if entry["source_token"] == end_token:
                    path = path[0:-1]
                    break

                if entry["target_index"] == 0:
                    path = []
                    break

                entry = dependency_group[entry["target_index"]]

            if len(path) > 0:
                paths.append(path)

        return paths


if __name__ == "__main__":

    p = DependencyParser()

    d = p.get_collapsed_dependencies("He ran really fast to his classroom. He was late to class, unfortunately.")

    print d

# EOF

