import unittest
from genisys.modules.nat import Nat
from genisys import configParser

class NatTest(unittest.TestCase):
    """ Tests for the NAT module """
    def test_values_in_config(self):
        """ Ensure that a missing config option raises the expected error. """
        with open("tests/configs/nat_test_1.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = Nat(config)
            with self.assertRaises(ValueError) as context:
                output = module.generate()    
    # end test_values_in_config

    def test_shared_interface_name(self):
        """ Ensure that interfaces sharing the same name raises an error. """
        with open("tests/configs/nat_test_2.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = Nat(config)
            with self.assertRaises(ValueError) as context:
                output = module.generate()

    # end test_shared_interface_name

    def test_expected_successful_output(self):
        expected_output = [
        "*nat",
        ":PREROUTING ACCEPT [0:0]",
        ":INPUT ACCEPT [0:0]",
        ":OUTPUT ACCEPT [0:0]",
        ":POSTROUTING ACCEPT [0:0]",
        "-A POSTROUTING -o eth02 -s 192.168.2.0/24 -j MASQUERADE",
        "COMMIT",
        "",
        "*filter",
        ":INPUT ACCEPT [0:0]",
        ":FORWARD ACCEPT [0:0]",
        ":OUTPUT ACCEPT [0:0]",
        "-P FORWARD ACCEPT",
        "-A FORWARD -i eth01 -o eth02 -j ACCEPT",
        "-A FORWARD -i eth02 -o eth01 -m state --state RELATED,ESTABLISHED -j ACCEPT",
        "COMMIT"
        ]
        with open("tests/configs/nat_test_3.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = Nat(config)
            output = module.generate().split("\n")
            for line in expected_output:
                self.assertIn(line, output)
    # end test_expected_successful_output

if __name__ == "__main__":
    unittest.main()
