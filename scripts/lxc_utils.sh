#!/bin/bash

aptProxy="192.168.55.100:3142"
sshKeyFile="/home/vagrant/.ssh/id_rsa.pub"

# Add SSH key from local file to container root user
# Parameters:
#   $1 => container name
#   $2 => fullpath to local file with public SSH key
addSSHKey () {
  name=${1:-"noname"}
  file=${2:-"nofile"}
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
  echo 'Acquire::http::Proxy "http://${aptProxy}";' | tee /etc/apt/apt.conf.d/02proxy
  apt-get install python-minimal aptitude -y
EOF

addSSHKey ${name} ${sshKeyFile}

}

# Prepare CentOs for ansible
# Parameters:
#   $1 => container name
prepareCentOs () {
  name=${1:-"noname"}
  lxc exec $name -- bash  <<EOF
  # cache with yum is inconsistent. Disabling it until a better solution is found
  # echo 'proxy=http://${aptProxy}' | tee --append /etc/yum.conf
  # sed -i 's/enabled=1/enabled=0/g' /etc/yum/pluginconf.d/fastestmirror.conf
  yum install -y openssh-server.x86_64
  # The command below will install the missing packages in the container to align the images.
  # This may be changes in the future to optimize the lab.
  # yum groups install -y "Minimal Install"
  systemctl start sshd
  systemctl enable sshd
EOF

addSSHKey ${name} ${sshKeyFile}

}

# Get IP for LXD container
# Parameters:
#   $1 => container name
getIp () {
  name=${1:-"noname"}
  ip=$(lxc list $name -c4 --format csv | grep eth0 |  cut -d' ' -f1 | sed -r 's/\"//g')
  echo "$ip"
}
