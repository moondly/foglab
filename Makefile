box-name := bento/ubuntu-18.04
box-version := 201906.18.0
devbox-name := devfoglab
devbox-build := foglab-build
hasBaseBox := $(shell vagrant box list | grep "$(box-name)" | grep $(box-version) | wc -l)
hasDevBox := $(shell vagrant box list | grep $(devbox-name) | wc -l)
hasBuildVmRunning := $(shell VBoxManage list runningvms | grep "$(devbox-build)" | wc -l)
hasBuildVm := $(shell VBoxManage list vms | grep "$(devbox-build)" | wc -l)

.PHONY: build test clean

build : foglab.json provision.yml
ifeq ($(strip $(hasBaseBox)),)
				vagrant box add $(box-name) --provider virtualbox --box-version $(box-version)
endif
				packer build -force foglab.json

add : ./build/package.box
				vagrant box add devfoglab ./build/package.box --force

test : 
				vagrant up --provision-with test
				vagrant destroy -f

clean : 
				rm -rf ./build/*.box
				rm -rf ./build/.vagrant
				vagrant destroy -f
ifeq ($(strip $(hasDevBox)),1)
				vagrant box remove devfoglab
else
				$(info No $(devbox-name) box to remove)
endif
ifeq ($(strip $(hasBuildVmRunning)),1)
				VBoxManage controlvm "$(devbox-build)" poweroff soft
else
				$(info No $(devbox-build) vm is running)
endif
ifeq ($(strip $(hasBuildVm)),1)
				VBoxManage unregistervm --delete "$(devbox-build)"
else
				$(info No $(devbox-build) vm is created)
endif

