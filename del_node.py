#! /usr/bin/python

# This tool will delete a node from the NODES list of a given config file if found
# The key is the name given at the time of creation (the key for the json object)

from optparse import OptionParser
import os
import json

__author__="root"
__date__ ="$Aug 2, 2015 Aug 2, 2015 7:40:06 PM$"
def usage_msg():
    return '''
    This tool is designed to be used with SSHCommander to delete nodes
    from the configuration. It will rewrite the config with the node removed.\n\n
    '''

c_file = ""
def list_nodes():
    global c_file
    try:
        print "opening %s" % c_file
        with open(c_file) as data_file:    
            data = json.load(data_file)
            print "\nNODE LIST FROM %s:\n" % c_file
            ki = 0
            for k in data["NODES"].keys():
                print "\033[1;34m\t\t"+str(ki)+". "+k+" ("+data["NODES"][k]['address']+")"+"\033[1;m"
                ki +=1
            print "\n"
         
    except Exception as e:
        print 'There was a problem getting the node list...'
        print e.message
        exit(1)

def remove_node(nn):
    global c_file
    out_nodes = {}
    try:
        with open(c_file,'r') as f:
            data = json.load(f)
            nodes = data["NODES"]
            
        for name in nodes.keys():
            print "checking %s" % name
            node_def = nodes[name]
            if name == nn:
                print node_def
                print "Removed from Config"
            else:
                out_nodes[name] = node_def
                
        data["NODES"] = out_nodes
        with open(c_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print e.message
        exit(1)

def exit_func():
    print '''\033[1;34m
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
                                  
                    \033[1;m'''
    print "Thanks for Shopping with B0n3.sec"
    exit(0)

if __name__ == "__main__":
    parser = OptionParser()
    def_conf = os.path.dirname(os.path.realpath(__file__)) + "/conf/config.json"
    parser.add_option("-c", "--conf-file", dest="conf_file", default=def_conf,
                      help="The JSON config file to update (%s)" % def_conf)
    
    (options, args) = parser.parse_args()
    print "\033[1;34m"+usage_msg()+"\033[1;m"
    c_file = options.conf_file
    list_nodes()
    node_name = raw_input("Node Name to DELETE > ")
    remove_node(node_name)
    exit_func()