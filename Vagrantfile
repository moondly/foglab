# Make sure this value do not overlap with any local network. Change it if necessary.
base_segment = '192.168.99'

Vagrant.configure("2") do |config|
  config.vm.box = "devfoglab"
  config.vm.network "private_network", ip: "#{base_segment}.100", adapter_ip: "#{base_segment}.1", netmask: "255.255.255.0", auto_config: false

  config.vm.synced_folder "localActions/", "/opt/foglab/localActions"
  config.vm.synced_folder "scripts/", "/opt/foglab/scripts"
  config.vm.synced_folder "examples/", "/opt/foglab/examples"
  config.vm.synced_folder "test/", "/opt/foglab/test"

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.provision "test", type: "shell", run: "never" do |s|
    s.inline = "echo Running tests... && python /opt/foglab/test/test.py"
  end

end
