import unittest
import subprocess
from subprocess import Popen, PIPE
from shlex import split

class TestStringMethods(unittest.TestCase):

    # Run command using shell and return stdout
    def rso(self, cmd):
        process = Popen(cmd, stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        return stdout.strip()

    # Run command using shell and return response code
    def rsr(self, cmd):
        resp = subprocess.call(cmd, shell=True)
        return resp

    def test_baseip_set(self):
        self.assertEqual(self.rsr("foglab baseip 192.168.11"), 0)
        self.assertEqual(self.rso("ip addr show dev lxdbr0 | grep 192.168.11.100 | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | grep 192.168.11 | wc -l"), '1')
        # unset
        self.assertEqual(self.rsr("foglab baseip 192.168.99"), 0)
        self.assertEqual(self.rso("ip addr show dev lxdbr0 | grep 192.168.99.100 | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | wc -l"), '1')
        self.assertEqual(self.rso("grep FOGLAB_BASE_IP_SEGMENT /etc/profile.d/foglab.sh | grep 192.168.99 | wc -l"), '1')

    def test_eth1_on(self):
        self.assertEqual(self.rsr("foglab eth1 on"), 0)
        self.assertEqual(self.rso("ip link show dev eth1 | grep UP | wc -l"), '1')

    def test_eth1_off(self):
        self.assertEqual(self.rsr("foglab eth1 off"), 0)
        self.assertEqual(self.rso("ip link show dev eth1 | grep UP | wc -l"), '0')

    def test_swap_on(self):
        self.assertEqual(self.rsr("foglab swap on"), 0)
        self.assertEqual(self.rso("cat /proc/swaps | wc -l"), '2')

    def test_swap_off(self):
        self.assertEqual(self.rsr("foglab swap off"), 0)
        self.assertEqual(self.rso("cat /proc/swaps | wc -l"), '1')
    
    # TODO: Add tests for lab

if __name__ == '__main__':
    unittest.main()