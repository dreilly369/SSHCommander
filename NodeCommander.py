import paramiko
import threading
import glob
import subprocess
import os
import time

class NodeCommander(threading.Thread):
    
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
    def connect_node(self):
        print "%s %s" % (self.node['key_path'],self.node['pass'])
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
        print "mv %s %s" % (base+"/"+script_path,base+"/"+new_name)
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
            print "custom/%s/*.cmdr" % ip
            files = glob.glob("custom/%s/*.cmdr" % ip)
            fcnt = len(files)
            print "Found %d Files for %s" % (fcnt,ip)
            return files
        except Exception as e:
            print 'There is no custom folder for %s, or it is inaccessible. Skipping' % ip
            print e.message
            return None
        
        return files
    
    def sftp_xfer(self, ssh_client, cmd_str):
        sftp = ssh_client.open_sftp()
        sftp.put(src, dst)
    
    def wait_for_it(self,seconds):
        time.sleep(seconds) # delays for x seconds
    
    def run(self):
        flist = self.get_file_list()
      
        if flist is None or len(flist) < 1:
            print "No Custom Scripts for %s" % self.node['address']
            return
        c = self.connect_node()
        print "connected"

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
        c.close()