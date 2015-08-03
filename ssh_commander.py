#! /usr/bin/python

# This connects to an SSH server using a public/private key pair.
# Upon a successful connection, it will run a given comd, or
# series of commands.

import paramiko
import subprocess
import os
import sys
import glob
import json
from NodeCommander import NodeCommander
import socket
import threading

__author__="D. Reilly"
__date__ ="$May 17, 2015 May 17, 2015 6:52:19 PM$"

class CommanderThread (threading.Thread):
    
    def __init__(self, threadID, node):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.node = node
        
                        
        self.failed_banner = '''
                  .-""""""-.
                .'          '.
               /   O      O   \\\t
              :           `    :
          oni |           `    | sad
              :    .------.    :
               \  '        '  /
                '.          .'
                  '-......-'
        '''
    
    def ipFromHost(self,remoteServer):
        socket.gethostbyname(remoteServer)
        
    def run(self):
        print '%s managing: %s' % (self.threadID,self.node["address"])
        self.run_commander()
        return
        
    
    
    def archive_script(self,script_path):
        line = subprocess.check_output(['tail', '-1', script_path])
        print line
        if line.startswith("%"):
            new_name = script_path.replace('.cmdr', '.bkp')
            subprocess.check_output(['mv %s %s' % (script_path,new_name) ])

    def ssh_command(self,cmds):
        split = self.node['address'].split(":")
        ip=split[0]
        port = '22'
        if len(split) > 0:
            port = split[1]
            
        addr=self.node['address']
        user=self.node['username']
        pwd=self.node['pass']
        key=self.node['key_path']

        print "Running Script"
        try:
            client = paramiko.SSHClient()
            client.load_host_keys('/root/.ssh/known_hosts')
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey = paramiko.RSAKey.from_private_key_file(key,pwd)
            transport = paramiko.Transport((ip, int(port)))
            transport.connect(username = user, pkey = pkey)
            ssh_session = transport.open_session()
        except Exception as e:
            print "Transport layer connection failure"
            exit(1)
        print "Connected to host"
        
        for cmd in cmds:
            try:
                print "Checking: %s" % cmd
                if (cmd[0] != "#" ) and (cmd[0] != "%" ):
                    print "Issuing: %s " % cmd
                    
                    if ssh_session.active:
                        status,output = client.run('pwd')
                        print "Command Sent"
                        

                else:
                    print "%s not a command" % cmd
                                
            except Exception as e:
                # @type cmd str
                print e
                print "Error sending command %s" % cmd
            return

    def run_commander(self):
        files = {}
        ip=self.node['address'].split(":")[0]
        try:
            files = glob.glob("custom/%s/*.cmdr" % ip)
            fcnt = len(files)
            print 'Running %d Custom Scripts for %s' % (fcnt,ip)
        except Exception:
            print 'There is no custom folder for %s, or it is inaccessible. Skipping' % self.node['address']

        if len(files) > 0:
            for fi in files:
                print "Script %s" % fi
                try:
                    lines = open(fi,'r').readlines()
                    self.ssh_command(lines)
                            
                    self.archive_script(fi)
                except Exception as e:
                    print 'There was a problem running the script...'
                    print "\n"+e.message+"\n"
                    print e.errno
                    print e.strerror
                    print self.failed_banner


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
            node = nodes[n]
            t = NodeCommander("Thread-%s" % i,node)
            threads.append(t)
            t.start()
        # Wait for all threads to complete
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print "You pressed Ctrl+C"
        sys.exit()