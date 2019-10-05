#!/bin/bash

# Add SSH key from local file to container root user
# Parameters:
#   $1 => container name
addSSHKey () {
  name=${1:-"noname"}

  sshPubKeyFile="/home/vagrant/.ssh/foglab.pub"

  # use the vagrant public key for all LXC images
  if [ ! -f ${sshPubKeyFile} ]; then
    grep vagrant /home/vagrant/.ssh/authorized_keys | tee ${sshPubKeyFile}
  fi

  chmod 644 ${sshPubKeyFile}

  dest=/root/id_rsa.pub
  lxc file push $sshPubKeyFile $name/$dest
  lxc exec $name -- bash  <<EOF
  cd ~
  mkdir -p .ssh
  chmod 700 .ssh/
  cat $dest >> .ssh/authorized_keys
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

addSSHKey ${name} 

}

# Prepare CentOs for ansible
# Parameters:
#   $1 => container name
prepareCentOs () {
  name=${1:-"noname"}
  lxc exec $name -- bash  <<EOF
  yum install -y openssh-server.x86_64
  systemctl start sshd
  systemctl enable sshd
EOF

addSSHKey ${name}

}
