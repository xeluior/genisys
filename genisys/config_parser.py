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

    def printDict(self: Self, dictionary) -> None:
        for key in dictionary:
            print(f"{key}: {dictionary[key]}")
    # end printDict

# end YAMLParser

def main():
    parser = YAMLParser('example.yml') 
    print(parser.get_all_headings())
    for eachSection in parser.get_all_headings():
        parser.printDict(parser.get_section(eachSection))

if __name__ == '__main__':
    main()
