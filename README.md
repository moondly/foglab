## Foglab is...
Foglab uses a combination of technologies like LXD, Terraform and Ansible to provide a local "cloud" lab ("fog" = low cloud). You can use Foglab to create multiple machines (LXD + Terraform) as well as automating the provisioning of those machines (Ansible).

## Using the vagrant box
1. Install `vagrant` and `virtualbox`
1. Create a `Vagrantfile` with the content below:

    ```
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
    ```

    You can adapt the `cpu` and `memory` accordingly. Please adapt the IP `base_segment` if it overlaps with any other local network. Your labs will receive IPs from the range `<base_segment>.101-254.`
    
    The `eth1` interface allows you to connect to the LXD hosts from your local machine. 
    
    You can use or not `swap` depending on the system memory available. Please notice that some applications may force swap to be disabled (kubernetes for instance).

1. Start and login:
    ```
    vagrant up
    vagrant ssh
    ``` 
1. Deploy your first lab
    ```
    mkdir mylab
    cd mylab
    cp /opt/foglab/examples/lab101.tf .
    terraform init
    terraform apply
    ```
1. Check the status:
    ```
    lxc list
    ```

1. Connect from you local machine

    Note the IP from `lxc list` and connect from your local machine using SSH and the vagrant private key:
    ```
    vagrant ssh-config | grep IdentityFile 
    
    ssh root@<ip> -i <IdentityFile>
    ```
  
1. Destroy it
    ```
    terraform destroy
    ```

### To pause/resume foglab
```
vagrant suspend
vagrant up
```

### To destroy foglab
```
vagrant destroy
```

# Developers
## Building a local vagrant basebox
To build a vagrant basebox do:
1. Make sure you have VirtualBox, Vagrant and Packer installed
1. Clone the git repo locally
1. While inside the repo folder type:
    ```
    packer build -force foglab.json
    ```
1. The image will be created under the `build` folder

You can then import the image to Vagrant like below:
```
vagrant box add myimage build/package.box
```

After that, you can use Vagrant normally and reference `myimage` as the source.

## No man is an island...
This would not be possible without the great work and nice ideas from:

- Terraform (https://www.terraform.io/)
- Vagrant (https://www.vagrantup.com/)
- Ansible (https://www.ansible.com/)
- Virtualbox (https://www.virtualbox.org/wiki/VirtualBox)
- Terraform LXD Provider (https://github.com/sl1pm4t/terraform-provider-lxd/)
- Terraform Inventory (https://github.com/adammck/terraform-inventory)
- http://chef.github.io/bento

Thanks guys!

