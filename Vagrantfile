# Make sure this value do not overlap with any local network. Change it if necessary.
base_segment = '192.168.55'

Vagrant.configure("2") do |config|
  config.vm.box = "moondly/foglab"
  config.vm.network "private_network", ip: "#{base_segment}.100", adapter_ip: "#{base_segment}.1", netmask: "255.255.255.0", auto_config: false

  config.vm.provider "virtualbox" do |v|
    v.memory = 8192
    v.cpus = 4
  end

  # Will configure the eth1 interface (-i on), activate the system swap (-s on) and configure the base_segment (-b)
  config.vm.provision "shell",
    inline: "foglab -i on && foglab -s on && foglab -b #{base_segment}"

end