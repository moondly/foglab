#!/bin/bash

sshPubKeyFile="/home/vagrant/.ssh/id_rsa.pub"

# use the vagrant public key for all LXC images
grep vagrant /home/vagrant/.ssh/authorized_keys | tee ${sshPubKeyFile}
chmod 644 ${sshPubKeyFile}

# Add SSH key from local file to container root user
# Parameters:
#   $1 => container name
#   $2 => fullpath to local file with public SSH key
addSSHKey () {
  name=${1:-"noname"}
  file=${2:-"nokey"}
  dest=/root/id_rsa.pub
  lxc file push $file $name/$dest
  lxc exec $name -- bash  <<EOF
  cd ~
  mkdir -p .ssh
  chmod 700 .ssh/
  cat $dest > .ssh/authorized_keys
  chmod 600 .ssh/authorized_keys
EOF
}

# Prepare Ubuntu for ansible
# Parameters:
#   $1 => container name
prepareUbuntu () {
  name=${1:-"noname"}
  lxc exec $name -- bash  <<EOF
  apt-get update
  apt-get install python-minimal -y
EOF

addSSHKey ${name} ${sshPubKeyFile}

}

# Prepare CentOs for ansible
# Parameters:
#   $1 => container name
prepareCentOs () {
  name=${1:-"noname"}
  lxc exec $name -- bash  <<EOF
  yum install -y openssh-server.x86_64 ntp
  systemctl start sshd
  systemctl enable sshd
EOF

addSSHKey ${name} ${sshPubKeyFile}

}

# Get IP for LXD container
# Parameters:
#   $1 => container name
getIp () {
  name=${1:-"noname"}
  ip=$(lxc list $name -c4 --format csv | grep eth0 |  cut -d' ' -f1 | sed -r 's/\"//g')
  echo "$ip"
}
