## Foglab is...
Foglab uses a combination of technologies like LXD, Terraform and Ansible to provide a local "cloud" lab ("fog" = low cloud). You can use Foglab to create multiple machines (LXD + Terraform) as well as automating the provisioning of those machines (Ansible).

## Architecture
![foglab](./support/foglabDiagram.png "Foglab architecture")

## Using foglab
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

      # Will configure the eth1 interface, activate the system swap and configure the base_segment
      config.vm.provision "shell",
        inline: "fogctl eth1 on && fogctl swap on && fogctl baseip #{base_segment}"

    end
    ```

    You can adapt the `cpu` and `memory` accordingly. Please adapt the IP `base_segment` if it overlaps with any other local network. If not specified, your machines will receive IPs from the range `<base_segment>.101-254.`
    
    The `eth1` interface allows you to connect to the LXD hosts from your local machine. 
    
    You can use or not `swap` depending on the system memory available. Please notice that some applications may force swap to be disabled (kubernetes for instance).

1. Start and login:
    ```
    vagrant up
    vagrant ssh
    ``` 
You are now ready to start creating your own labs in foglab!

### Commands to manage `foglab`
#### To pause/resume foglab
```
vagrant suspend
vagrant up
```

#### To destroy foglab
```
vagrant destroy
```

### Commands to manage `labs` (while inside foglab)
#### Make sure you are inside foglab. If not:
```
vagrant ssh
```
#### Deploy a lab with 2 machines
1. Create a folder to contain you lab
    ```
    mkdir mylab
    ```
1. You need to be inside your lab folder to manage the lab
    ```
    cd mylab
    ```
1. Create the lab config folder and apply it
    ```
    fogctl lab -n 2 -a
    
    # >> Check the changes and type "yes" when requested
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
    ```
    This will create a file called `lab.tf` used by terraform to deploy the machines. Type `fogctl lab -h` to check all options. 
    
    NOTE: The machine names are defined using this pattern: `<labname>[01-99]`. Ex: mylab01, mylab02, ...
1. List the current machine status:
    ```
    fogctl lab -l
    ```
You can manually edit the `lab.tf` file and apply using `fogctl lab -a`
#### Change the number of machines but do not apply automatically
1. Make sure you are inside your lab:
    ```
    cd mylab
    ```
1. Change the config but do not apply. Use -f to force the change (lab.tf already exists at this point):
    ```
    fogctl lab -n 3 -f
    ```
1. When you are ready, apply the change:
    ```
    fogctl lab -a

    # >> Check the changes and type "yes" when requested

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

#### Destroy the lab
1. Make sure you are inside your lab:
    ```
    cd mylab
    ```
1. Destroy the lab:
    ```
    fogctl lab --destroy

    # >> Check the changes and type "yes" when requested
    ```

#### Connect from you local command time to the machines

1. Get the IPs for your machines
    ```
    fogctl lab -l
    ```

1. From you local command line (in the same folder as `Vagrantfile`):
    ```
    vagrant ssh-config | grep IdentityFile 
    
    ssh root@<ip> -i <IdentityFile>
    ```
    TIP: It is always a good idea to install your own public key in the machines so you don't have to use `-i` every time. 


# For Developers
## Building a local vagrant basebox
To build a vagrant basebox do:
1. You will need `VirtualBox`, `Vagrant`, `Packer` and `make` installed
1. Clone the git repo locally
1. Build the image, add to Vagrant and test:
    ```
    make
    make add
    make test
    ```
1. Bring up a the dev image built:
    ```
    vagrant up
    ```
1. To remove all created artifacts (images, vagrant boxes, etc):
    ```
    make clean
    ```
The following directories will be mapped during development:
* folder `localActions/` mapped to: `/opt/foglab/localActions`
* folder `scripts/` mapped to: `/opt/foglab/scripts`
* folder `examples/` mapped to: `/opt/foglab/examples`
* folder `test/` mapped to: `/opt/foglab/test`

During image build, the content of the directories are copied to the respective folders inside the image.

