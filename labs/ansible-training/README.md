# Ansible Training Lab
This lab can be used to get you comfortable with Ansible. The information is mainly related to the Lynda.com training "Ansible Essentials".

# Setup Your Lab Environment
A distinction can be made between 3 environments in this setup:
- The host: This is your laptop or similar where the Vagrant box is running on.
- The box or VM: This is the Vagrant box provisioning and hosting the systems.
- The lab: The provisioned systems and/or infrastructure on top of the VM.

## Starting the box/VM
Prepare and start the box (VM) as mentioned in the [main README.md](../../README.md)

## Building the lab: Infrastructure from the VM
The lab is provisioned and started from inside the VM by running the following commands:
```
vagrant ssh
sudo su -
cd /vagrant/labs/<your lab>/
terraform plan
terraform apply
```

This brings up the following LXD systems reachable from the host.
| Hostname 	| Private IP     	| Description 	|
|----------	|----------------	|-------------	|
| web1     	| 192.168.55.181 	| Web Server  	|
| web2     	| 192.168.55.182 	| Web Server  	|
| db1      	| 192.168.55.191 	| Database    	|
| db2      	| 192.168.55.192 	| Database    	|

## Ansible directly from the host
Ansible will be executed from the host system and will talk directly to the LXD systems. The Vagrant box can be seen as completely transient. This is automatically realized by forwarding the public SSH key from the Vagrant box to the LXD systems.

In the host system (e.g. on your MAC BookPro) install ansible via brew
```
brew install ansible
```

Get the ssh <vagrant_private_key> location as per the the description in the [main README.md](../../README.md)

Prepare the ssh keys in your `~./ssh/config`, where <vagrant_private_key> is the ssh <vagrant_private_key> location found above.
```
# web1
host 192.168.55.181
 HostName 192.168.55.181
 IdentityFile <vagrant_private_key>
 User root
# web2
host 192.168.55.182
 HostName 192.168.55.182
 IdentityFile <vagrant_private_key>
 User root
# db1
host 192.168.55.191
 HostName 192.168.55.191
 IdentityFile <vagrant_private_key>
 User root
# db2
host 192.168.55.192
 HostName 192.168.55.192
 IdentityFile <vagrant_private_key>
 User root
```

First, login manually to each host to add the footprint to the known_hosts.
```
ssh root@<ip>
```

At this point ansible can be executed directly against the above mentioned hosts.

# Training Notes
The most exercises are around creating temp files to demonstrate the functionality of ansible. What works well is to watch a directory on the LXD host for addition and removal of these files as follows:
```
ssh root@<ip>
watch -t 'ls -a /tmp/ | grep file'
```
Exercises are executed initially with something similar like (example):
```
ansible-playbook -i ../../inventory 2-1-tasks.yml -e file_state=touch
```

## Cleanup
The following steps should be taken to delete the entire lab setup.
- Delete entries from `~./ssh/config`
- Delete entries from `~./ssh/known_hosts`
- For destroying the lab itself, including the underlying VM/box, please refer to the [main README.md](../../README.md) for more information
