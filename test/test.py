import unittest
import subprocess
from subprocess import Popen, PIPE
import os
import shutil

# Run command using shell and return stdout
def rso(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    stdout, stderr = process.communicate()
    return stdout.strip().decode('UTF-8')

# Run command using shell and return response code
def rsr(cmd):
    resp = subprocess.call(cmd, shell=True)
    return resp

class TestFogCtlGeneral(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        rsr("fogctl baseip 192.168.11")

    def test_baseip_set(self):
        self.assertEqual(rsr("fogctl baseip 192.168.22"), 0)
        self.assertEqual(rso("ip addr show dev lxdbr0 | grep 192.168.22.100 | wc -l"), '1')
        self.assertEqual(rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | wc -l"), '1')
        self.assertEqual(rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | grep 192.168.22 | wc -l"), '1')

    def test_eth1_on(self):
        self.assertEqual(rsr("fogctl eth1 on"), 0)
        self.assertEqual(rso("ip link show dev eth1 | grep UP | wc -l"), '1')

    def test_eth1_off(self):
        self.assertEqual(rsr("fogctl eth1 off"), 0)
        self.assertEqual(rso("ip link show dev eth1 | grep UP | wc -l"), '0')

    def test_swap_on(self):
        self.assertEqual(rsr("fogctl swap on"), 0)
        self.assertEqual(rso("cat /proc/swaps | wc -l"), '2')

    def test_swap_off(self):
        self.assertEqual(rsr("fogctl swap off"), 0)
        self.assertEqual(rso("cat /proc/swaps | wc -l"), '1')
    
class TestFogCtlVm(unittest.TestCase):
    testDir = "/tmp/testVm"
    labName = os.path.basename(testDir)

    @classmethod
    def setUpClass(cls):
        try:
            os.makedirs(cls.testDir)
        except OSError:
            print ("Creation of the directory %s failed" % cls.testDir)
    
    @classmethod
    def tearDownClass(cls):
        try:
            rsr("cd %s && terraform destroy -auto-approve" % cls.testDir)
            shutil.rmtree(cls.testDir)
        except OSError as e:
            pass

    def test_01_vm_create(self):
        self.assertEqual(rsr("cd %s && fogctl vm -n 2 -a --approve" % self.testDir), 0)
        self.assertEqual(rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % self.labName), '2')
        
    def test_02_vm_modify(self):
        self.assertEqual(rsr("cd %s && fogctl vm -n 3 -a -f --approve" % self.testDir), 0)
        self.assertEqual(rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % self.labName), '3')
        
    def test_03_vm_destroy(self):
        self.assertEqual(rsr("cd %s && fogctl vm --destroy --approve" % self.testDir), 0)
        self.assertEqual(rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % self.labName), '0')
        self.assertFalse(os.listdir('%s' % self.testDir))

class TestFogCtlSnapshot(unittest.TestCase):
    testDir = "/tmp/testSnap"
    labName = os.path.basename(testDir)

    @classmethod
    def setUpClass(cls):
        try:
            os.makedirs(cls.testDir)
        except OSError:
            print ("Creation of the directory %s failed" % cls.testDir)
        
        rsr("cd %s && fogctl vm -n 2 -a --approve" % cls.testDir)
    
    @classmethod
    def tearDownClass(cls):
        try:
            rsr("cd %s && terraform destroy -auto-approve" % cls.testDir)
            shutil.rmtree(cls.testDir)
        except OSError as e:
            pass

    def test_01_snapshot_create(self):
        self.assertEqual(rsr("cd %s && fogctl snapshot create --label snap1" % self.testDir), 0)
        self.assertEqual(rso("cd %s && fogctl snapshot list | grep snap1 | wc -l" % self.testDir), '2')
        
    def test_02_snapshot_restore(self):
        self.assertEqual(rsr("cd %s && fogctl snapshot restore --label snap1" % self.testDir), 0)
        
    def test_03_snapshot_delete(self):
        self.assertEqual(rsr("cd %s && fogctl snapshot delete --label snap1" % self.testDir), 0)
        self.assertEqual(rso("cd %s && fogctl snapshot list | grep snap1 | wc -l" % self.testDir), '0')
        

class TestFogCtlSshKey(unittest.TestCase):
    testDir = "/tmp/testSshKey"
    labName = os.path.basename(testDir)

    @classmethod
    def setUpClass(cls):
        try:
            os.makedirs(cls.testDir)
        except OSError:
            print ("Creation of the directory %s failed" % cls.testDir)
    
    @classmethod
    def tearDownClass(cls):
        try:
            rsr("cd %s && terraform destroy -auto-approve" % cls.testDir)
            shutil.rmtree(cls.testDir)
        except OSError as e:
            pass

    def test_01_add(self):
        self.assertEqual(rsr("cd %s && fogctl sshkey --key sshkey1" % self.testDir), 0)
        self.assertEqual(rso("grep sshkey1 /home/vagrant/.ssh/foglab.pub | wc -l"), '1')

    def test_02_create_vm_with_key(self):
        self.assertEqual(rsr("cd %s && fogctl vm -n 2 -a --approve" % self.testDir), 0)
        self.assertEqual(rso("lxc list %s[0-9]+ -cn --format csv | wc -l" % self.labName), '2')
        self.assertEqual(rso("lxc exec %s grep sshkey1 /root/.ssh/authorized_keys | wc -l" % (self.labName+"01")), '1')

    def test_03_add_in_lab(self):
        self.assertEqual(rsr("cd %s && fogctl sshkey --key sshkey2 --lab" % self.testDir), 0)
        vms = rso("lxc list -cn --format csv %s[0-9]+" % self.labName).split()
        for vm in vms:
            self.assertEqual(rso("lxc exec %s grep sshkey2 /root/.ssh/authorized_keys | wc -l" % vm), '1')



if __name__ == '__main__':
    unittest.main()