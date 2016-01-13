
""" This is used as a test to ensure lvg works.
    The compile java code is used within metamap.
"""

import subprocess

# command i need to execute
# java -cp $CLASS_PATHS ApiTest.NormApiTest

CLASS_PATHS = ".:lvg/lib/*"
JAVA_PATH   = "LvgNormApi.Norm"

def lvgNormalize(strings):

    stdout = subprocess.check_output(["java", "-cp", CLASS_PATHS, JAVA_PATH] + strings)

    stdout = stdout.split('\n')[0:-1]

    norm = [phrases.split('|') for phrases in stdout]

    if len(norm) != len(strings):

        exit("error: mismatched number of normalized string groups and strings")

    return norm

if __name__ == "__main__":

    print lvgNormalize(["dirtiest", "bleeding"])


