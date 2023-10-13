import yaml # Look into using ruamel.yaml for using YAML 1.2 specification
from typing import Self

class YAMLParser:
    def __init__(self, fileName) -> None:
        self.fileName = fileName
    # end __init__

    ''' Returns all of the key value pairs under a specific heading as a Python dictionary '''
    def getSection(self: Self, heading):
        dictionary = {}
        with open(self.fileName) as file:
            data = yaml.safe_load(file)

            if heading in data:
                sectionData = data[heading]
                print('Current Heading: ' + heading)

                try:
                    for key, value in sectionData.items():
                        dictionary[key] = value
                except AttributeError:
                    print('Heading', heading, 'contains no values.')

            else:
                print('Heading \'' + heading + '\' not found.')
        
        return dictionary
    # end getSection

    ''' Returns a list object containing all section headings in the provided YAML file '''
    def getAllHeadings(self: Self):
        headingList = []
        with open(self.fileName) as file:
            data = yaml.safe_load(file)

            for heading in data:
                headingList.append(heading)

        return headingList
    # end getAllHeadings

    def printDict(self: Self, dictionary):
        for key in dictionary:
            print(f"{key}: {dictionary[key]}")
    # end printDict

def main():
    parser = YAMLParser('test.yml') 
    print(parser.getAllHeadings())
    for eachSection in parser.getAllHeadings():
        parser.printDict(parser.getSection(eachSection))

if __name__ == '__main__':
    main()