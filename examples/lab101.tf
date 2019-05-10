provider "lxd" {
}

# Example Ubuntu LXD
resource "lxd_container" "node1" {
  name      = "node1"
  image     = "ubuntu:18.04"
  ephemeral = false
  profiles  = ["default"]
  limits {
    cpu = "1"
    memory = "1GB"
  }

  config {
    user.access_interface = "eth0"  # Default interface to be reported in terraform show
  }

  # Using a fixed IP
  device {
    name = "eth0"
    type = "nic"
    properties {
      nictype = "bridged"
      parent = "lxdbr0"
      ipv4.address = "192.168.55.180"
    }
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareUbuntu ${lxd_container.node1.name}"
  }
  
}

# Example CentOs LXD
resource "lxd_container" "node2" {
  name      = "node2"
  image     = "images:centos/7"
  ephemeral = false
  profiles  = ["default"]
  limits {
    cpu = "1"
    memory = "1GB"
  }

  config {
    user.access_interface = "eth0"
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareCentOs ${lxd_container.node2.name}"
  }
}