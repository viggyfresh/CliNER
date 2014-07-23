######################################################################
#  CliCon - read_config.py                                           #
#                                                                    #
#  Willie Boag                                      wboag@cs.uml.edu #
#                                                                    #
#  Purpose: Read a configuration file to determine what features     #
#               are available on the system                          #
######################################################################



import os



# Enabled modules
class enabled_modules:

    # Unenabled unless specified by config file
    UMLS  = False
    GENIA = False



#
# available_services()
#
# @return dictionary of (name,on/off) pairs.
#
#                       ex. {'UMLS': False, 'GENIA': True}
#
def available_services():

    # Open config file
    prefix = os.path.dirname(__file__)
    filename = os.path.join( prefix, 'features.config' )
    f = open(filename, 'r')

    specs = {}
    module_list = [ 'GENIA', 'UMLS' ]


    for line in f.readlines():
        words = line.split()
        if words:

            # Modules
            if words[0] ==  'UMLS': enabled_modules.UMLS  = (words[1] == 'True')
            if words[0] == 'GENIA': enabled_modules.GENIA = (words[1] == 'True')

            # retVal dict
            if words[0] in module_list:
                specs[words[0]] = (words[1] == 'True')

    return specs



# Read from config file when module is imported
#print available_services()


