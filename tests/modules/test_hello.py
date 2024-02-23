import unittest
from genisys.modules.firstboot.hello import Hello
from genisys import config_parser

class HelloModuleTest(unittest.TestCase):
    """Tests for the Hello module"""
    def test_ssl_config_values_present(self):
        """Test that the ssl option is correctly detected"""
        expected_output_list = [
            '#!/bin/bash',
            'apt update && apt install iproute2 gawk coreutils curl jq',
            'ip_addr="$(ip -o -4 show scope global | awk \'{print $4}\' | cut -d/ -f1 | head -n1)',
            'jq --null-input --arg ip "${ip_addr}" \'{message: "hello", ip: $ip}\' > ip.json',
            'hostname="$(curl --json @ip.json https://10.0.0.1:15206 | jq -r \'.hostname\')"',
            '[ "$hostname" != "null" ] && hostnamectl set-hostname "$hostname"'
        ]

        with open("tests/configs/hello_test_1.yml", encoding='utf-8') as config_file:
            config = config_parser.YAMLParser(config_file.name)
            module = Hello(config)

            output = module.generate().split("\n")
            for line in expected_output_list:
                self.assertIn(line, output)

    def test_ssl_config_values_not_present(self):
        """Test that the ssl option is correctly detected, opposite of test 1"""
        expected_output_list = [
            '#!/bin/bash',
            'apt update && apt install iproute2 gawk coreutils curl jq',
            'ip_addr="$(ip -o -4 show scope global | awk \'{print $4}\' | cut -d/ -f1 | head -n1)',
            'jq --null-input --arg ip "${ip_addr}" \'{message: "hello", ip: $ip}\' > ip.json',
            'hostname="$(curl --json @ip.json http://10.0.0.1:15206 | jq -r \'.hostname\')"',
            '[ "$hostname" != "null" ] && hostnamectl set-hostname "$hostname"'
        ]

        with open("tests/configs/hello_test_2.yml", encoding='utf-8') as config_file:
            config = config_parser.YAMLParser(config_file.name)
            module = Hello(config)

            output = module.generate().split("\n")
            for line in expected_output_list:
                self.assertIn(line, output)
