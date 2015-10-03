#! /usr/bin/python

# Add a node to the SSHCOmmander
# config and generate a key for it.
# Password auth is req'd to push the key and update the config file.

import json
import subprocess 
import random
from optparse import OptionParser
import os
import errno
from os import chmod
from Crypto.PublicKey import RSA 
from random import Random  
import getpass
import paramiko

__author__="D. Reilly"
__date__ ="$Aug 2, 2015 Aug 2, 2015 2:09:08 PM$"

def usage_msg():
    return '''
    This tool is designed to be used with SSHCommander to add nodes
    to the configuration. It will generate a new SSH key. It can optionally add the
    new key to the node's authorized_keys folder. Finally you may have
    SSHCommander update the sshd_config on the node to lock the login to prevent
    further password logins. This function is currently EXPERIMENTAL. It can break sshd_conf. 
    For now a backup of the sshd_conf should be created\n\n
    '''

def gen_random_pass(length):
    return ''.join(random.choice('0123456789ABCDEFabcdefghijklmnopqrstuvwxyz_-') for i in range(length))

def get_key_password():
    keypass = '';
    minlen = 16 # Must be greater that 8 by ssh-keygen rules...but why skimp?
    while len(keypass) < minlen:
       keypass = raw_input("Enter Password for new key (%d char min or r for random) > " % minlen) 
       if keypass is 'r' or keypass is 'R':
           keypass = gen_random_pass(minlen)
    return keypass

def get_address_parts(node):
        parts = node['address'].split(':')
        if len(parts) < 2:
            parts.append(22)
        else:
            parts[1] = int(parts[1])
        print parts
        return [parts[0],parts[1]]

def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def push_key_to_node(node,keyname):
    goforit = raw_input("add key to %s [y/n]> " % node['address'])
    if goforit in ["y","Y"]:
        logpass = getpass.getpass(prompt='Login Password > ')
        nip,nport = get_address_parts(node)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(nip, port=nport, username=node['username'], password=logpass)
        client.exec_command('mkdir -p ~/.ssh/')
        client.exec_command('echo "%s" > ~/.ssh/authorized_keys' % keyname)
        client.exec_command('chmod 644 ~/.ssh/authorized_keys')
        client.exec_command('chmod 700 ~/.ssh/')
        print "Key added to %s" % nip
    else:
        print "Skipping upload.\n You will need to do this manually before SSHCommander will work"
        return

def key_path(dir,name):
    if dir[:-1] is "/":
        return dir+name
    else:
        return dir+"/"+name
    
def generate_node_key(node_name,loc,passwd):
    privkf = key_path(loc,node_name)
    print subprocess.call("ssh-keygen -f %s -N %s -t rsa" % (privkf, passwd), shell=True)
    
def add_nodes_to_conf(new_nodes,conf_file,nc=0):
    try:
        f_loc = os.path.dirname(os.path.realpath(__file__))+"/"+conf_file
        if not os.path.isfile(f_loc):
            print "creating %s" % f_loc
            open(f_loc, 'w').close() 
        with open(f_loc,'r') as f:
            try:
                data = json.load(f)
                nodes = data["NODES"]
            except Exception:
                data = {"NODES":{}}
                nodes = data["NODES"]
            
        for name in new_nodes.keys():
            node_def = new_nodes[name]
            print node_def
            nodes.update({name:node_def})
        data["NODES"] = nodes
        with open(conf_file, 'w') as f:
            json.dump(data, f)
    except Exception as e: 
        print e
        exit(1)

def make_path_exist(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        
def def_nodes(conf_file):
    enter_again = True
    new_nodes = {}
    while enter_again:
        name = raw_input("Node name > ")
        addr = raw_input("Node address (including :port_num if not 22) > ")
        uname = raw_input("Node Username > ")
        keydir = raw_input("local Dir to create key in > ")
        keypass = get_key_password()
        new_node = {
            "username": uname,
            "pass": keypass,
            "key_path": key_path(keydir,name),
            "address": addr
        }
        generate_node_key(name,keydir,keypass)
        push_key_to_node(new_node,name)
        new_nodes[name] = new_node
        ip,port = get_address_parts(new_node)
        make_path_exist("custom/%s" % name)
        again = uname = raw_input("Add another Node? (y/n) > ")
        if again.lower() != "y":
            enter_again = False
            print "Finishing"
    add_nodes_to_conf(new_nodes,conf_file)
    
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
                      help="The JSON config file to update or create default (%s)" % def_conf)
    parser.add_option("-l", "--list-nodes", dest="list_nodes", default=None,
                      help="List nodes in a given config and exit")
    (options, args) = parser.parse_args()
    
    if options.list_nodes is not None:
        try:
            with open(options.list_nodes) as data_file:    
                data = json.load(data_file)
                print "\nNODE LIST FROM %s:\n" % options.list_nodes
                ki = 0
                for k in data["NODES"].keys():
                    print "\033[1;34m\t\t"+str(ki)+". "+k+" ("+data["NODES"][k]['address']+")"+"\033[1;m"
                    ki += 1
                print "\n"
            exit_func()    
        except Exception:
            print 'There was a problem getting the node list...'
            exit(1)

    print "\033[1;34m"+usage_msg()+"\033[1;m"
    def_nodes(options.conf_file)
    exit_func()