import yaml # Look into using ruamel.yaml for using YAML 1.2 specification
from typing_extensions import Self

class YAMLParser:
    def __init__(self, filename) -> None:
        self.filename = filename
    # end __init__

    def getSection(self: Self, heading: str) -> dict:
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
                raise Exception('Heading not found.')
        
        return dictionary
    # end getSection

    def getAllHeadings(self: Self) -> list:
        ''' Returns a list object containing all section headings in the provided YAML file '''
        headings = []
        with open(self.filename, encoding='utf-8') as file:
            data = yaml.safe_load(file)

            for heading in data:
                headings.append(heading)

        return headings
    # end getAllHeadings

    def printDict(self: Self, dictionary) -> None:
        for key in dictionary:
            print(f"{key}: {dictionary[key]}")
    # end printDict

# end YAMLParser

def main():
    parser = YAMLParser('example.yml') 
    print(parser.getAllHeadings())
    for eachSection in parser.getAllHeadings():
        parser.printDict(parser.getSection(eachSection))

if __name__ == '__main__':
    main()
