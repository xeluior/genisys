# add the src dir to python path
import sys
import os

current_dir = os.path.dirname(__file__)
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'genisys'))
sys.path.insert(0, src_dir)

# okay now the tests actually start
from modules.netplan import Netplan
import unittest
import yaml

class NetplanTests(unittest.TestCase):
    def test_netmask_eq_cidr(self):
        config = {
            "subnet": "10.0.0.0/24",
            "netmask": "255.255.254.0" # prefix len 23
        }
        module = Netplan(config)
        with self.assertRaises(ValueError) as err:
            module.generate()
        self.assertEqual(err.exception.args[0], "Subnet mask does not match CIDR prefix length")

    def test_ip_in_subnet(self):
        config = {
            "subnet": "10.0.0.0/24",
            "ip": "192.168.0.1"
        }
        module = Netplan(config)
        with self.assertRaises(ValueError) as err:
            module.generate()
        self.assertEqual(err.exception.args[0], "IP is not in the given subnet")

    def test_expected_yaml(self):
        expected = yaml.dump({"network": {"ethernets": {"eth0": {"addresses": ["10.0.0.1/24"]}}}})
        config = {
            "interface": "eth0",
            "ip": "10.0.0.1",
            "subnet": "10.0.0.0",
            "netmask": "255.255.255.0"
        }
        module = Netplan(config)
        self.assertEqual(expected, module.generate())

if __name__ == "__main__":
    unittest.main()
    
