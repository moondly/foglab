#!/usr/bin/env python3

import argparse
import subprocess
from subprocess import Popen, PIPE
from pathlib import Path
import os
import os.path
import shutil

home = Path.home()
DROPLET_DIR=os.path.join(os.sep,home,".droplets")
DROPLET_GITREPO="https://github.com/moondly/droplets.git"
DROPLET_ROLES_DIR=os.path.join(os.sep,DROPLET_DIR,"drops")
LOCAL_ACTIONS_DIR=os.path.join(os.sep,"opt","foglab","localActions")

# Run command using shell and return stdout
def rso(cmd):
  process = Popen(cmd, stdout=PIPE, shell=True)
  stdout, stderr = process.communicate()
  return stdout.strip().decode('UTF-8')

# Run command using shell and return response code
def rsr(cmd):
    resp = subprocess.call(cmd, shell=True)
    return resp

def init(args):

  if args.update:
    resp = rsr("cd %r && git pull" % (DROPLET_DIR))
    if resp != 0:
      print("Could not pull git (CODE: %s)" % resp)
      raise SystemExit
  else:
    resp = rsr("git clone %r %r" % (DROPLET_GITREPO, DROPLET_DIR))
    if resp != 0:
      print("Could not clone git (CODE: %s)" % resp)
      raise SystemExit

  print("Done!")
  

def apply(args):
  currDir = os.getcwd()
  playbook = LOCAL_ACTIONS_DIR + "/droplet.yml"
  name = args.name
  requirements = os.path.join(os.sep,DROPLET_ROLES_DIR,name,"requirements.yml")
  mainFile = os.path.join(os.sep,DROPLET_ROLES_DIR,name,"apply.yml")
  deployToDir = os.path.join(os.sep,currDir,name)
  rolesPath = ["~/.ansible/roles","/usr/share/ansible/roles","/etc/ansible/roles", DROPLET_ROLES_DIR]

  print("Creating droplet: %r" % name)

  # Install prereq
  if os.path.isfile(requirements):
    rsr("ansible-galaxy install -r %r" % (requirements))
  # Local actions
  extra = "{'droplet_name': %r, 'dir': %r, 'droplet_dir': %r}" % (name, currDir, DROPLET_DIR)
  rsr("ansible-playbook %r --extra-vars %r" % (playbook, extra))
  # Infra deployment
  rsr("cd %r && fogctl vm -a --approve" % (deployToDir))
  # Remote actions
  rsr("cd %r && ANSIBLE_ROLES_PATH=%r ansible-playbook -i .hosts %r -u root " % (deployToDir,":".join(rolesPath),mainFile))
  # Info
  rsr("cd %r && cat %r" % (deployToDir, "README"))

def destroy(args):
  currDir = os.getcwd()
  name = args.name
  deployToDir = os.path.join(os.sep,currDir,name)
  print("Remove droplet: %r" % name)

  if not os.path.isdir(deployToDir):
      print("No droplet %r fount at %r" % (name, deployToDir))
      raise SystemExit

  rsr("cd %r && fogctl vm --destroy --approve" % (deployToDir))

  try:
    shutil.rmtree(deployToDir)
  except OSError as e:
    pass

  print("Done!")

# Argument parser
parser = argparse.ArgumentParser(prog='dropctl')
subparsers = parser.add_subparsers(title='subcommands')

parser_swap = subparsers.add_parser('init')
parser_swap.add_argument('--update', action='store_true', default=False , help='Checkout the latest changes from the droplet remote repo')
parser_swap.set_defaults(func=init)


parser_create = subparsers.add_parser('apply')
parser_create.add_argument('name', type=str, help='The droplet name')
parser_create.add_argument('-i', choices=['ubuntu:18.04', 'centos/7'], default='ubuntu:18.04', help='The image to use. Default: ubuntu:18.04. TODO: detect from lab.tf!!')
parser_create.set_defaults(func=apply)

parser_destroy = subparsers.add_parser('destroy')
parser_destroy.add_argument('name', type=str, help='The droplet name to destroy')
parser_destroy.set_defaults(func=destroy)

args = parser.parse_args()
if not hasattr(args, 'func'):
  print("No options were passed. Try -h for help")
  raise SystemExit

args.func(args)



