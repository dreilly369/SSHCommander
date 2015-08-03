![SSH Terminal](http://www.pc-freak.net/images/ssh-how-to-login-with-password-provided-from-command-line-use-sshpass-to-run-same-command-to-forest-of-linux-servers.png "SSHCommander 1")

# SSHCommander
SSHCommander is a multi-threaded python based utility to control network nodes via SSH using Paramiko. It uses encrypted Public/Private keys to securely log in to each node. More features are planned....If I get around to them :) For now, it works for most basic use cases. It is limited by the quirks of Paramiko, but that has not really limited me. 

## Setup
SSHCommander uses the Paramiko module to connect to remote nodes via Private Key SSH Tunnels. So you need to have a couple pieces on the Command controller:

###Python 2.7
SSHCommander is currently designed and tested for Linux clusters. Most modern versions of Linux come with Python 2.7 installed. You can verify your version with:
   `python -v`
   
###Paramiko
   `pip install paramiko`
   
###SSH
Again, most Linux systems come with SSH pre-installed. To configure SSH to be usable by SSHCommander you need to have a couple settings changed. Update your sshd_config as follows:
```
PermitEmptyPasswords no
ChallengeResponseAuthentication no
PasswordAuthentication no
X11Forwarding no
LoginGraceTime 5
PermitRootLogin yes
StrictModes yes
RSAAuthentication yes
PubkeyAuthentication yes
```
These changes allow root login which I typically do not support. I make an exception here because restricting the login type to Key pair only. For production systems, it is not strictly required. If you do not want SSHCommander to log in as root, you can make an sshcommander user, and fine tune it's access that way.

###config.json
SSHCommander uses a JSON config to keep track of node information. The configuration of a Node is relatively self explanatory but I will include an example here anyway:
```
{
    "NODES": {
        "node-1":{
            "username": "root",
            "pass": "PrivateKeyPassword1",
            "key_path": "/var/www/security/node-1",
            "address":"192.168.0.127:2369"
        },
        "node-2":{
            "username": "root",
            "pass": "PrivateKeyPassword2",
            "key_path": "/root/.ssh/node-2",
            "address": "192.168.0.107"
        }
    },
    "FOLDERS":{
        "known_hosts":"/root/.ssh/known_hosts"
    }
    
}
```
*Note: The custom port for node-1 is given as `192.168.0.127:2369`
*Note: Additional sections, like FOLDERS, are for expansion purposes. They are not currently used and can safely be ignored.

## Usage
Using SSHCommander to manage nodes is as easy as placing a script in a directory. SSHCommander runs continuously, looking for .cmdr scripts to run. There are two classes of scripts: Custom and Common. I will cover them in a minute, first to actually run the system: change to the directory you cloned SSHCommander in to, then run with:
`python ssh_commander.py`

###Custom
Custom scripts are placed under the `custom/<address>/` directory. They will be run on the corresponding node only.

###Common
These scripts are placed in the `common/` directory and will be run on every node in the config.

### One Shot vs. Repeater
Some scripts you may only want to run once (or once in a while). SSHCommander allows this by archiving scripts. It will rename the script extension fron .cmdr to .bkp 
To make a script archive after it is run simply add a `%` as the last line of the file. For common scripts the archiving is deffered until all threads return to avoid a race condition where some node would archive the script before another node would request the common scripts.

## Contribute
If you look and this and say "I could do better" I say, yeah probably. Please do. And then send me a PR for bonus karma. Some features and bugs I am looking to handle are:
+ Paramiko Client does not like to `cd` unless it is in one line with all other commands for that dir 
i.e. `cd /opt; pwd; ls -al`
+ If address is HostName, resolve with socket module.
+ Add logging. Yeah logs would probably be nice.
+ Add interactive mode...a.k.a One Shell To Rule Them All *IN PROGRESS*
+ That bugse you find that I haven't even thought of.
