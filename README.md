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

### Managing `foglab`
#### To pause/resume foglab
```
vagrant suspend
vagrant up
```

#### To destroy foglab
```
vagrant destroy
```

### Managing `labs`
#### Make sure you are inside foglab. If not:
```
vagrant ssh
```
#### Add your ssh public key
```
fogctl sshkey

Please enter the ssh public key to use: <type you ssh public key>
```
NOTE: if you do not set a public key, the public key from vagrant will be used. Check `fogctl sshkey -h` for more options.
#### Deploy a lab with 2 machines
1. Create a folder to contain your lab
    ```
    mkdir mylab
    ```
1. You need to be inside your lab folder to manage the lab
    ```
    cd mylab
    ```
1. Create the vms
    ```
    fogctl vm -n 2 -a
    
    # >> Check the changes and type "yes" when requested
    
    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
    ```
    This will create a file called `lab.tf` used by terraform to deploy the machines. Type `fogctl vm -h` to check all options. 
    
    NOTE: The machine names are defined after the folder name like: `<labname>[01-99]`. Ex: mylab01, mylab02, ...
1. List the current machine status:
    ```
    fogctl vm -l
    ```
You can manually edit the `lab.tf` file and apply using `fogctl vm -a`
#### Change the number of vms but do not apply automatically
1. Make sure you are inside your lab:
    ```
    cd mylab
    ```
1. Change the config but do not apply. Use -f to force the change (lab.tf already exists at this point):
    ```
    fogctl vm -n 3 -f
    ```
1. When you are ready, apply the changes:
    ```
    fogctl vm -a

    # >> Check the changes and type "yes" when requested

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

#### Snapshots
It is always a good itde to save snapshots from your lab so you can go back in time if something goes wrong.
1. Make sure you are inside your lab:
    ```
    cd mylab
    ```
* To create a snapshot:
    ```
    fogctl snapshot create --label snap1

    Snapshot for vm 'mylab01' created with label 'snap1' at '2019-10-05T21:44:53Z'
    Snapshot for vm 'mylab02' created with label 'snap1' at '2019-10-05T21:44:54Z'
    ```
* To list a snapshot:
    ```
    fogctl snapshot list

    Snapshots for 'mylab01':
      'snap1' : '2019-10-05T21:44:53Z'
    Snapshots for 'mylab02':
      'snap1' : '2019-10-05T21:44:54Z'
    ```
* To retsore a snapshot:
    ```
    fogctl snapshot restore --label snap1

    Vm 'mylab01' restored to snapshot with label 'snap1'
    Vm 'mylab02' restored to snapshot with label 'snap1'
    ```
Check `fogctl snapshot -h` for more options.
#### Destroy the lab
1. Make sure you are inside your lab:
    ```
    cd mylab
    ```
1. Destroy the lab:
    ```
    fogctl vm --destroy

    # >> Check the changes and type "yes" when requested
    ```

#### Connect from you local terminal to the vms

1. Get the IPs for your machines
    ```
    fogctl vm -l
    ```
1. If you used your own ssh public key, from your `local terminal` type:
    ```
    ssh root@<ip> 
    ```
1. If not, use the vagrant ssh key:
    ```
    vagrant ssh-config | grep IdentityFile 
    
    ssh root@<ip> -i <IdentityFile>
    ```


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

During the image build, the content of the directories are copied to the respective folders inside the image.

