#! /usr/bin/python

# This connects to a cluster of SSH servers using public/private key pairs.
# Upon a successful connection, it will run a given comd, or
# series of commands.

import subprocess
import os
import sys
import glob
import json
from NodeCommander import NodeCommander
from optparse import OptionParser

__author__="D. Reilly"
__date__ ="$May 17, 2015 May 17, 2015 6:52:19 PM$"

def load_nodeset(nodeList):
    global config
    try:
        with open(nodeList) as data_file:    
            data = json.load(data_file)
        return data["NODES"]
        if config.empty():
            config = data
    except Exception:
        print 'There was a problem getting the node list...'
        exit(1)
    
def archive_common_dir():
    try:
        files = glob.glob("common/*.cmdr")
        fcnt = len(files)
        for file in files:
            line = subprocess.check_output(['tail', '-1', file])
            if line.startswith("%"):
                file = os.path.realpath(file)
                new_name = file.replace('.cmdr', '.bkp')
                os.rename(file, new_name)
    except Exception:
        raise

banner = '''
                               _,.-----.,_
                            ,-~           ~-.
                           ,^___           ___^.
                          /~"   ~"   .   "~   "~\

                         | Y     ~-. | ,-~     Y |
                         | |        }:{        | |
                         j l       / | \       ! l
                      .-~  (__,.--" .^. "--.,__)  ~-.
                     (           / / | \ \           )
                      \.____,   ~  \/"\/  ~   .____,/
                       ^.____                 ____.^
                          | |T ~\  !   !  /~ T| |
                          | |l   _ _ _ _ _   !| |
                          | l \/V V V V V V\/ j |
                          l  \ \|_|_|_|_|_|/ /  !
                           \  \[T T T T T TI/  /
                            \  `^-^-^-^-^-^'  /
                             \               /
                              \.           ,/
                                "^-.___,-^"

                    ,-.   ,-.  .  . ,--,               
                    |  ) /  /\ |\ |   /                
                    |-<  | / | | \|  `.    ,-. ,-. ,-. 
                    |  ) \/  / |  |    )   `-. |-' |   
                    `-'   `-'  '  ' `-'  o `-' `-' `-' 

                        '''
if __name__ == "__main__":
    parser = OptionParser()
    def_conf = os.path.dirname(os.path.realpath(__file__)) + "/conf/config.json"
    parser.add_option("-c", "--conf-file", dest="conf_file", default=def_conf,
                      help="The JSON config file to update or create default (%s)" % def_conf)
    
    (options, args) = parser.parse_args()
    
    nodes = load_nodeset(options.conf_file)
    threads = []
    node_count = len(nodes)
    try:
        print "Firing off %d Threads" % node_count
        for i in range(node_count):
            n = nodes.keys()[i]
            #print n
            node = nodes[n]
            t = NodeCommander("Thread-%s" % i, n, node)
            threads.append(t)
            t.start()
        # Wait for all threads to complete
        for t in threads:
            t.join()
        archive_common_dir()
    except KeyboardInterrupt:
        print "You pressed Ctrl+C"
        sys.exit()