import paramiko
import threading
import glob
import subprocess
import os
import time

class NodeCommander(threading.Thread):
    
    def __init__(self, threadID, nodeID, node):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.node = node
        self.nodeID = nodeID
                        
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
    def connect_node(self):
        k = paramiko.RSAKey.from_private_key_file(self.node['key_path'],self.node['pass'])
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ip,pt = self.get_address_parts()
        try:
            c.connect( hostname = ip, port=pt, username = self.node['username'], pkey = k )
            return c
        except Exception as e:
            print "Failed to connect to %s" % (self.node['address'])
            print e.message
            print self.failed_banner
            return
        
    def is_special(self,cmd):
        commands = {
            "XFER": ""
        }
        
    def archive_script(self,script_path):
        new_name = script_path.replace('.cmdr', '.bkp')
        base = os.path.dirname(os.path.realpath(__file__))
        src = base+"/"+script_path
        dst = base+"/"+new_name
        os.rename(src,dst)

    def get_address_parts(self):
        parts = self.node['address'].split(':')
        if len(parts) < 2:
            parts.append(22)
        else:
            parts[1] = int(parts[1])
        print parts
        return [parts[0],parts[1]]
    
    def get_file_list(self):
        files = {}
        ip,port = self.get_address_parts()
        try:
            files = glob.glob("custom/%s/*.cmdr" % self.nodeID)
            fcnt = len(files)
            print "Found %d Files for %s (%s)" % (fcnt, self.nodeID, ip)
            return files
        except Exception as e:
            print 'There is no custom folder for %s, or it is inaccessible. Skipping' % ip
            print e.message
            return None
        
        return files
    
    def run_dir(self,dirstr):
        try:
            flist = glob.glob(dirstr+"*.cmdr") #dirstr
            fcnt = len(flist)
            
        except Exception:
            raise
        
        c = self.conn
        i = 0
        while i < len(flist):
            file = str(flist[i])
            base = os.path.dirname(os.path.realpath(__file__))
            lines = open(base+'/'+file,'r').readlines()
            print lines
            archive_me = False
            #Send commands to node if they are not handled locally or comments
            for command in lines:
                if command is "%" :
                    archive_me = True
                elif command[0] is "#":
                    continue
                elif self.is_special(command):
                    continue
                else:
                    print "Executing {}".format( command )
                    stdin , stdout, stderr = c.exec_command(command)
                    print stdout.read()
                    errs = stderr.read()
                    if errs is not None:
                        print( "Errors:")
                        print errs
            if archive_me and not "common" in dirstr:
                print "Archiving %s" % file
                self.archive_script(file)
            i += 1
    
    def run_custom_dir(self,flist):
        c = self.conn
        i = 0
        while i < len(flist):
            file = str(flist[i])
            base = os.path.dirname(os.path.realpath(__file__))
            lines = open(base+'/'+file,'r').readlines()
            print lines
            archive_me = False
            #Send commands to node if they are not handled locally or comments
            for command in lines:
                if command is "%" :
                    archive_me = True
                elif command[0] is "#":
                    continue
                elif self.is_special(command):
                    continue
                else:
                    print "Executing {}".format( command )
                    stdin , stdout, stderr = c.exec_command(command)
                    print stdout.read()
                    errs = stderr.read()
                    if errs is not None:
                        print( "Errors:")
                        print errs
            if archive_me:
                print "Archiving %s" % file
                self.archive_script(file)
            i += 1
    def sftp_xfer(self, ssh_client, cmd_str):
        sftp = ssh_client.open_sftp()
        sftp.put(src, dst)
    
    def wait_for_it(self,seconds):
        time.sleep(seconds) # delays for x seconds
    
    def run(self):
        self.conn = self.connect_node()
        print "connected"
        self.run_dir("common/")
        ip,port = self.get_address_parts()
        cust_dir = "custom/%s/" % ip
        self.run_dir(cust_dir)
        self.conn.close()