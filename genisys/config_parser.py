import os
from ipaddress import IPv4Address
import yaml # Look into using ruamel.yaml for using YAML 1.2 specification
from typing_extensions import Self

class YAMLParser:
    """Parses a YAML config file and provides helper methods to access it's contents"""
    def __init__(self, filename) -> None:
        self.filename = filename
    # end __init__

    def get_section(self: Self, heading: str) -> dict:
        '''Returns all of the key value pairs under a specific heading as a Python dictionary'''
        dictionary = {}
        with open(self.filename, encoding='utf-8') as file:
            data = yaml.safe_load(file)

            if heading in data:
                section_data = data[heading]

                try:
                    for key, value in section_data.items():
                        dictionary[key] = value
                except AttributeError:
                    print("Heading is empty.")

            else:
                return {}

        # If being run in a github runner environment, we need to get
        # the new network/IP values at run time.
        if 'GITHUB_RUNNER' in os.environ:
            runner_ip = os.environ['RUNNER_IP']
            # Assign IP of server
            dictionary['ip'] = str(IPv4Address(runner_ip))
            # Create (estimated) network/subnet value
            octets = runner_ip.split('.')
            network_addr = '.'.join([octets[0], octets[1], octets[2], '0'])
            dictionary['subnet'] = network_addr + '/24'
            # Create (estimated) DHCP range
            dictionary['dhcp-ranges'] = network_addr + ',' + str(str(IPv4Address(runner_ip) + 10))

        return dictionary
    # end get_section

    def get_all_headings(self: Self) -> list:
        ''' Returns a list object containing all section headings in the provided YAML file '''
        headings = []
        with open(self.filename, encoding='utf-8') as file:
            data = yaml.safe_load(file)

            for heading in data:
                headings.append(heading)

        return headings
    # end get_all_headings

    def print_dict(self: Self, dictionary) -> None:
        """Helper function to pretty print a dictionary"""
        for key in dictionary:
            print(f"{key}: {dictionary[key]}")
    # end printDict

    def as_dict(self: Self) -> dict:
        """ Convert YAML to dictionary """
        whole_config = {}
        for section in self.get_all_headings():
            whole_config[section] = self.get_section(section)

        return whole_config
    # end as_dict
# end YAMLParser

def main():
    """Load a test config and parse it"""
    parser = YAMLParser('example.yml')
    print(parser.get_all_headings())
    for each_section in parser.get_all_headings():
        parser.print_dict(parser.get_section(each_section))

if __name__ == '__main__':
    main()
