provider "lxd" {}

# web1
resource "lxd_container" "web1" {
  name      = "web1"
  image     = "ubuntu:18.04"
  ephemeral = false
  profiles  = ["default"]

  limits {
    cpu    = "1"
    memory = "512MB"
  }

  config {
    user.access_interface = "eth0" # Default interface to be reported in terraform show
  }

  # Using a fixed IP
  device {
    name = "eth0"
    type = "nic"

    properties {
      nictype      = "bridged"
      parent       = "lxdbr0"
      ipv4.address = "192.168.55.181"
    }
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareUbuntu ${lxd_container.web1.name}"
  }
}

# web2
resource "lxd_container" "web2" {
  name      = "web2"
  image     = "ubuntu:18.04"
  ephemeral = false
  profiles  = ["default"]

  limits {
    cpu    = "1"
    memory = "512MB"
  }

  config {
    user.access_interface = "eth0" # Default interface to be reported in terraform show
  }

  # Using a fixed IP
  device {
    name = "eth0"
    type = "nic"

    properties {
      nictype      = "bridged"
      parent       = "lxdbr0"
      ipv4.address = "192.168.55.182"
    }
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareUbuntu ${lxd_container.web2.name}"
  }
}

# db1
resource "lxd_container" "db1" {
  name      = "db1"
  image     = "ubuntu:18.04"
  ephemeral = false
  profiles  = ["default"]

  limits {
    cpu    = "1"
    memory = "512MB"
  }

  config {
    user.access_interface = "eth0" # Default interface to be reported in terraform show
  }

  # Using a fixed IP
  device {
    name = "eth0"
    type = "nic"

    properties {
      nictype      = "bridged"
      parent       = "lxdbr0"
      ipv4.address = "192.168.55.191"
    }
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareUbuntu ${lxd_container.db1.name}"
  }
}

# db2
resource "lxd_container" "db2" {
  name      = "db2"
  image     = "ubuntu:18.04"
  ephemeral = false
  profiles  = ["default"]

  limits {
    cpu    = "1"
    memory = "512MB"
  }

  config {
    user.access_interface = "eth0" # Default interface to be reported in terraform show
  }

  # Using a fixed IP
  device {
    name = "eth0"
    type = "nic"

    properties {
      nictype      = "bridged"
      parent       = "lxdbr0"
      ipv4.address = "192.168.55.192"
    }
  }

  provisioner "local-exec" {
    command = ". /opt/foglab/scripts/lxc_utils.sh && prepareUbuntu ${lxd_container.db2.name}"
  }
}
