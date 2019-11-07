#!/usr/bin/env python3

import argparse
import subprocess
from subprocess import Popen, PIPE
from pathlib import Path
import os
import os.path
import shutil

USER_HOME = Path.home()
DROP_LIB_DIR=os.path.join(os.sep,USER_HOME,".droplets")
DROP_GITREPO="https://github.com/moondly/droplets.git"
DROP_ROLES_DIR=os.path.join(os.sep,DROP_LIB_DIR,"drops")
ANSIBLE_ROLES_PATH=["~/.ansible/roles","/usr/share/ansible/roles","/etc/ansible/roles", DROP_ROLES_DIR]
LOCAL_ACTIONS_DIR=os.path.join(os.sep,"opt","foglab","localActions")

CURRENT_DIR = os.getcwd()
PUBLISH_HOSTS_DIR = os.path.join(os.sep,CURRENT_DIR,".droplets")

# Run command using shell and return stdout
def rso(cmd):
  process = Popen(cmd, stdout=PIPE, shell=True)
  stdout, stderr = process.communicate()
  return stdout.strip().decode('UTF-8')

# Run command using shell and return response code
def rsr(cmd):
    return int(subprocess.call(cmd, shell=True))

def init(args):

  if args.update:
    resp = rsr("cd %r && git pull" % (DROP_LIB_DIR))
    if resp != 0:
      print("Could not pull git (CODE: %s)" % resp)
      raise SystemExit
  else:
    resp = rsr("git clone %r %r" % (DROP_GITREPO, DROP_LIB_DIR))
    if resp != 0:
      print("Could not clone git (CODE: %s)" % resp)
      raise SystemExit

  print("Done!")
  

def runAnsible(name, deployDir, playbook, user="root"):
  extraVars = "{'home': %r, 'drop_home': %r, 'drop_name': %r, 'drop_lib_dir': %r}" % (CURRENT_DIR, deployDir, name, DROP_LIB_DIR)
  return rsr("ANSIBLE_ROLES_PATH=%r ansible-playbook %r -i %r -u %r --extra-vars %r" % (":".join(ANSIBLE_ROLES_PATH), playbook, PUBLISH_HOSTS_DIR, user, extraVars))

def apply(args):
  name = args.name
  phases = args.phases
  
  print("Phases to run: %r" % phases)

  infraFile = os.path.join(os.sep,DROP_ROLES_DIR,name,"infra.tf")
  reqFile = os.path.join(os.sep,DROP_ROLES_DIR,name,"requirements.yml")
  preFile = os.path.join(os.sep,DROP_ROLES_DIR,name,"pre.yml")
  provFile = os.path.join(os.sep,DROP_ROLES_DIR,name,"provision.yml")
  posFile = os.path.join(os.sep,DROP_ROLES_DIR,name,"pos.yml")
  
  deployToDir = os.path.join(os.sep,CURRENT_DIR, name)

  print("Creating droplet: %r" % name)

  # Local actions
  if 'all' in phases or 'init' in phases:
    print("Init")
    # publish the hosts
    print(deployToDir)
    if not os.path.isdir(deployToDir):
      resp = rsr("mkdir %r" % deployToDir)

    # copy the infra file
    resp = rsr("cp %r %r" % (infraFile, os.path.join(os.sep, deployToDir, "infra.tf")))
    if resp != 0:
      print("INIT failed (CODE: %s)" % resp)
      raise SystemExit

  # Install req
  if 'all' in phases or 'req' in phases:
    if os.path.isfile(reqFile):
      resp = rsr("ansible-galaxy install -r %r" % (reqFile))
      if resp != 0:
        print("REQ failed (CODE: %s)" % resp)
        raise SystemExit

  # Run pre req
  if 'all' in phases or 'pre' in phases:
    if os.path.isfile(preFile):
      print("PRE phase")
      resp = runAnsible(name, deployToDir, preFile)
      if resp != 0:
        print("PRE failed (CODE: %s)" % resp)
        raise SystemExit
  
  # Infra deployment
  if 'all' in phases or 'infra' in phases:
    if os.path.isfile(infraFile):
      print("INFRA phase")
      resp = rsr("cd %r && fogctl vm -a --approve" % (deployToDir))
      if resp != 0:
        print("INFRA failed (CODE: %s)" % resp)
        raise SystemExit
    
      # publish the hosts
      if not os.path.isdir(PUBLISH_HOSTS_DIR):
        rsr("mkdir %r" % PUBLISH_HOSTS_DIR)
      
      # Publish the inventories using a symlink in PUBLISH_HOSTS_DIR
      rsr("ln -sf %r %r" % (os.path.join(os.sep, deployToDir, ".%s.hosts" % name), os.path.join(os.sep,PUBLISH_HOSTS_DIR,"%s.hosts" % name)))

  # Remote prov
  if 'all' in phases or 'prov' in phases:
    resp = runAnsible(name, deployToDir, provFile)
    if resp != 0:
      print("PROVISIONING failed (CODE: %s)" % resp)
      raise SystemExit
  # Run pos req
  if 'all' in phases or 'pos' in phases:
    if os.path.isfile(posFile):
      print("POS phase")
      resp = runAnsible(name, deployToDir, posFile)
      if resp != 0:
        print("POS failed (CODE: %s)" % resp)
        raise SystemExit

  # Info
  if 'all' in phases or 'info' in phases:
    resp = rsr("cd %r && cat %r" % (deployToDir, "README"))
    if resp != 0:
      print("Readme failed (CODE: %s)" % resp)
      raise SystemExit
  
  print("Done!")

def destroy(args):
  name = args.name.replace("/","")
  deployToDir = os.path.join(os.sep,CURRENT_DIR,name)

  print("Remove droplet: %r" % name)

  if not os.path.isdir(deployToDir):
      print("No droplet %r fount at %r" % (name, deployToDir))
      raise SystemExit

  rsr("cd %r && fogctl vm --destroy --approve" % (deployToDir))

  # published hosts
  publishedHostsFile = os.path.join(os.sep,PUBLISH_HOSTS_DIR,"%s.hosts" % name)
  if os.path.isfile(publishedHostsFile):
    rsr("rm %r" % publishedHostsFile)

  try:
    shutil.rmtree(deployToDir)
    if os.path.isdir(PUBLISH_HOSTS_DIR):
      n = rso("ls %r | wc -l" % PUBLISH_HOSTS_DIR)
      if n == "0":
        shutil.rmtree(PUBLISH_HOSTS_DIR)

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
parser_create.add_argument('--phases', nargs='+', choices=['all', 'init', 'req', 'pre', 'infra', 'prov', 'pos', 'info'], default=['all'], help='Phases to run')
parser_create.set_defaults(func=apply)

parser_destroy = subparsers.add_parser('destroy')
parser_destroy.add_argument('name', type=str, help='The droplet name to destroy')
parser_destroy.set_defaults(func=destroy)

args = parser.parse_args()
if not hasattr(args, 'func'):
  print("No options were passed. Try -h for help")
  raise SystemExit

args.func(args)



