import unittest
import subprocess
from subprocess import Popen, PIPE
import os
import shutil

class TestStringMethods(unittest.TestCase):

    # Run command using shell and return stdout
    def rso(self, cmd):
        process = Popen(cmd, stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        return stdout.strip().decode('UTF-8')

    # Run command using shell and return response code
    def rsr(self, cmd):
        resp = subprocess.call(cmd, shell=True)
        return resp

    def test_baseip_set(self):
        self.assertEqual(self.rsr("fogctl baseip 192.168.11"), 0)
        self.assertEqual(self.rso("ip addr show dev lxdbr0 | grep 192.168.11.100 | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | grep 192.168.11 | wc -l"), '1')
        # unset
        self.assertEqual(self.rsr("fogctl baseip 192.168.99"), 0)
        self.assertEqual(self.rso("ip addr show dev lxdbr0 | grep 192.168.99.100 | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | grep 192.168.99 | wc -l"), '1')

    def test_eth1_on(self):
        self.assertEqual(self.rsr("fogctl eth1 on"), 0)
        self.assertEqual(self.rso("ip link show dev eth1 | grep UP | wc -l"), '1')

    def test_eth1_off(self):
        self.assertEqual(self.rsr("fogctl eth1 off"), 0)
        self.assertEqual(self.rso("ip link show dev eth1 | grep UP | wc -l"), '0')

    def test_swap_on(self):
        self.assertEqual(self.rsr("fogctl swap on"), 0)
        self.assertEqual(self.rso("cat /proc/swaps | wc -l"), '2')

    def test_swap_off(self):
        self.assertEqual(self.rsr("fogctl swap off"), 0)
        self.assertEqual(self.rso("cat /proc/swaps | wc -l"), '1')
    
    def test_vm_and_snaphot(self):
        directory = "/tmp/testVmAndSnap"
        labName = os.path.basename(directory)
        try:
            os.makedirs(directory)
        except OSError:
            print ("Creation of the directory %s failed" % directory)
            

        # create
        self.assertEqual(self.rsr("cd %s && fogctl vm -n 2 -a" % directory), 0)
        self.assertEqual(self.rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % labName), '2')
        
        # snapshot create
        self.assertEqual(self.rsr("cd %s && fogctl snapshot create --label snap1" % directory), 0)
        self.assertEqual(self.rso("cd %s && fogctl snapshot list | grep snap1 | wc -l" % directory), '2')
        
        # snapshot restore
        self.assertEqual(self.rsr("cd %s && fogctl snapshot restore --label snap1" % directory), 0)
        
        # snapshot delete
        self.assertEqual(self.rsr("cd %s && fogctl snapshot delete --label snap1" % directory), 0)
        self.assertEqual(self.rso("cd %s && fogctl snapshot list | grep snap1 | wc -l" % directory), '0')
        # modify
        self.assertEqual(self.rsr("cd %s && fogctl vm -n 3 -a -f" % directory), 0)
        self.assertEqual(self.rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % labName), '3')
        
        # destroy
        self.assertEqual(self.rsr("cd %s && fogctl vm --destroy" % directory), 0)
        self.assertEqual(self.rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % labName), '0')
        self.assertFalse(os.listdir('%s' % directory))

        try:
            self.rsr("cd %s && terraform destroy -auto-approve" % directory)
            shutil.rmtree(directory)
        except OSError as e:
            True

if __name__ == '__main__':
    unittest.main()