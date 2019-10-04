#!/usr/bin/env python3

import argparse
import subprocess
from subprocess import Popen, PIPE
import re
import os
import os.path
import shutil
import json
import random
import string

LOCALACTIONSDIR=os.path.join(os.sep,"opt","foglab","localActions")

def typeIpv4(ip):
  if not re.search("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", ip):
    msg = "Invalid base ip %r. Ex: 192.168.55" % ip
    raise argparse.ArgumentTypeError(msg)
  return ip

def action(action, tags, extra=None):
  print('action: %s, tag: %s, extra: %s' % (action, tags, extra))
  playbook = LOCALACTIONSDIR + "/" + action + ".yml"
  
  extra = extra or ""
  subprocess.call(["ansible-playbook", playbook, "--tags", tags, "--extra-vars", extra])

def swap(args):
  action("swap", args.state)

def eth1(args):
  action("eth1", args.state)

def baseip(args):
  action("lxdip", "all", "base_segment="+args.baseip)

def vm(args):
  currdir = os.getcwd()
  configFile = "lab.tf"
  labName = os.path.basename(currdir)
  labConfigFile = os.path.join(currdir,configFile)

  if not args.n is None:
    if not args.f and os.path.isfile(labConfigFile):
      print("Config file %r exists. Use -f to force overwrite" % configFile)
      raise SystemExit

    image = args.i
    itype = "ubuntu"
    ip = args.ip if args.ip is not None else -1
    cpu = args.cpu
    mem = args.mem
    if re.search("centos", image):
      image = "images:"+image
      itype = "centos"
    action("tfTemplate", "create", "{'n': %d,'lab_name': %r, 'dir': %r, 'image': %r, 'type': %r, 'ip': %d, 'cpu' : %d, 'mem': %d}" % (args.n, labName, currdir, image, itype, ip, cpu, mem))

  if args.a:
    subprocess.call(["terraform", "init"])
    subprocess.call(["terraform", "apply", "-auto-approve"])
    subprocess.call(["lxc", "list", "%s[0-9]+" % labName])
  
  if args.l:
    subprocess.call(["lxc", "list", "%s[0-9]+" % labName])

  if args.destroy:
    subprocess.call(["terraform", "destroy", "-auto-approve"])
    for f in [labConfigFile, 'terraform.tfstate', 'terraform.tfstate.backup']:
      if os.path.isfile(f):
        os.remove(f)
    try:
      shutil.rmtree('.terraform')
    except OSError as e:
      True
    

# Run command using shell and return stdout
def rso(cmd):
  process = Popen(cmd, stdout=PIPE, shell=True)
  stdout, stderr = process.communicate()
  return stdout.strip().decode('UTF-8')

def lxcq(op, path):
  resp = json.loads(rso("lxc query -X %s %s" % (op.upper(), path)))
  return resp

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def snap(args):
  currdir = os.getcwd()
  labName = os.path.basename(currdir)
  action = args.action
  label = args.label if args.label is not None else randomString()
  vms = rso("lxc list -cn --format csv %s[0-9]+" % labName).split()
  for vm in vms:
    if action == "create":
      resp = subprocess.call(["lxc", "snapshot", vm, label])
      if resp == 0:
        info = lxcq("GET","/1.0/containers/%s/snapshots/%s" % (vm, label))
        print("Snapshot for vm %r created with label %r at %r" % (vm, label, info['created_at']))
    elif action == "restore":
      resp = subprocess.call(["lxc", "restore", vm, label])
      if resp == 0:
        print("Vm %r restored to snapshot with label %r" % (vm, label))
    elif action == "delete":
      resp = subprocess.call(["lxc", "delete", "%s/%s" % (vm,label)])
      if resp == 0:
        print("Snapshot for vm %r with label %r deleted" % (vm, label))
    elif action == "list":
      print("Snapshots for %r:" % vm)
      slist = lxcq("GET","/1.0/containers/%s/snapshots" % vm)
      for s in slist:
        sinfo = lxcq("GET","%s" % s)
        print("  %r : %r" % (sinfo['name'], sinfo['created_at']))

# Argument parser
parser = argparse.ArgumentParser(prog='foglab')
subparsers = parser.add_subparsers(title='subcommands')

parser_swap = subparsers.add_parser('swap')
parser_swap.add_argument('state', choices=['on', 'off'] , help='Enable or disable the swap')
parser_swap.set_defaults(func=swap)

parser_eth1 = subparsers.add_parser('eth1')
parser_eth1.add_argument('state', choices=['on', 'off'] , help='Enable or disable the eth1 interface')
parser_eth1.set_defaults(func=eth1)

parser_baseip = subparsers.add_parser('baseip')
parser_baseip.add_argument('baseip', type=typeIpv4 , help='The base ip segment to use. Ex: 192.168.55')
parser_baseip.set_defaults(func=baseip)

parser_vm = subparsers.add_parser('vm')
parser_vm.add_argument('-i', choices=['ubuntu:18.04', 'centos/7'], default='ubuntu:18.04', help='The image to use. Default: ubuntu:18.04')
parser_vm.add_argument('-n', type=int, help='The number of machines to create in the lab')
parser_vm.add_argument('-a', action='store_true', default=False, help='Apply the config')
parser_vm.add_argument('-f', action='store_true', default=False, help='Force the config creation')
parser_vm.add_argument('-l', action='store_true', default=False, help='Lab machines status')
parser_vm.add_argument('--destroy', action='store_true', default=False, help='Destroy all machines')
parser_vm.add_argument('--cpu', type=int, default=1, help='Number of cpus on each machine. Default: 1')
parser_vm.add_argument('--mem', type=int, default=256, help='Memory (MB) on each machine. Default: 256.')
parser_vm.add_argument('--ip', type=int, help='Use fixed IP for the machines starting with the value defined and incremented by 1 for each machine. Ex: 192.168.55.x, 192.168.55.(x+1), ...')
parser_vm.set_defaults(func=vm)

parser_snap = subparsers.add_parser('snapshot')
parser_snap.add_argument('action', choices=['create', 'restore', 'delete', 'list'], help='The snapshot action to take. Default: create')
parser_snap.add_argument('--label', help='The snapshot label. If not passed, a random string will be used')
parser_snap.set_defaults(func=snap)


args = parser.parse_args()
if not hasattr(args, 'func'):
  print("No options were passed. Try -h for help")
  raise SystemExit

args.func(args)



