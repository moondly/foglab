objects := foglab.json provision.yml
box-name := bento/ubuntu-18.04
box-version := 201906.18.0
devbox-name := devfoglab
devbox-build := foglab-build
hasBaseBox := $(shell vagrant box list | grep "$(box-name)" | grep $(box-version))
hasDevBox := $(shell vagrant box list | grep $(devbox-name))
hasBuildVmRunning := $(shell VBoxManage list runningvms | grep "$(devbox-build)")
hasBuildVm := $(shell VBoxManage list vms | grep "$(devbox-build)")

create : $(objects)
ifeq ($(strip $(hasBaseBox)),)
				vagrant box add $(box-name) --provider virtualbox --box-version $(box-version)
endif
				packer build -force foglab.json

add : ./build/package.box
				vagrant box add devfoglab ./build/package.box --force

.PHONY: test
test : 
				vagrant up --provision-with test

.PHONY: clean
clean : 
				rm -rf ./build/*.box
				rm -rf ./build/.vagrant
				vagrant destroy -f
ifneq ($(strip $(hasDevBox)),)
				vagrant box remove devfoglab
endif
ifneq ($(strip $(hasBuildVmRunning)),)
				VBoxManage controlvm "$(devbox-build)" poweroff soft
endif
ifneq ($(strip $(hasBuildVm)),)
				VBoxManage unregistervm --delete "$(devbox-build)"
endif

