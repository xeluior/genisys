import yaml # Look into using ruamel.yaml for using YAML 1.2 specification

''' Returns all of the key value pairs under a specific heading as a Python dictionary '''
def getSection(fileName, heading):
    dictionary = {}
    with open(fileName) as file:
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

''' Returns a list object containing all section headings in the provided YAML file '''
def getAllHeadings(fileName):
    headingList = []
    with open(fileName) as file:
        data = yaml.safe_load(file)

        for heading in data:
            headingList.append(heading)

    return headingList

def printDict(dictionary):
    for key in dictionary:
        print(f"{key}: {dictionary[key]}")

def main():
    print(getAllHeadings('test.yml'))
    for eachSection in getAllHeadings('test.yml'):
        printDict(getSection('test.yml', eachSection))

if __name__ == '__main__':
    main()