''' 
argv[1] = yaml file to parse 
argv[2] = section in yaml file to grab (If this is absent, return entire file as dictionary)
'''
import sys
import yaml # Look into using ruamel.yaml for using YAML 1.2 specification

''' Returns all of the key value pairs under a specific heading as a Python dictionary '''
def getSection(fileName, heading):
    dictionary = {}
    with open(fileName) as file:
        data = yaml.safe_load(file)

        if heading in data:
            sectionData = data[heading]

            for key, value in sectionData.items():
                dictionary[key] = value

        else:
            print('Heading \'' + heading + '\' not found.')
    
    return dictionary

# def getAllSections(fileName):
#     dictList = [{}]
#     with open(fileName) as file:
#         data = yaml.safe_load(file)

#         for heading in data:
#             sectionData = data[heading]

#             for key, value in sectionData.items():


def printDict(dictionary):
    for key in dictionary:
        print(f"{key}: {dictionary[key]}")

def main():
    if len(sys.argv) > 2:
        printDict(getSection(sys.argv[1], sys.argv[2]))
    else:
        print('unimplemented')


if __name__ == '__main__':
    main()