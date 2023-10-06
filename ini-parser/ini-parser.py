import configparser 
import pathlib

currentDirectory = pathlib.Path().resolve() # Returns windowsPath obj representing working directory (\genisys\)

''' Accepts a read config and converts it into a traditional python dictionary of strings object. If "removeComments" is true, comments will be stripped from the final dictionary. '''
def MakeDictionary(config, removeComments):
    
    
    if(removeComments):
        config = removeComments(config)
    

'''  '''
def removeComments(config):
    
    #TODO#
    # for section in config.sections():
    #     print((config[section]))

    return config


''' Prints out the entire content of a ConfigParser object to the console as key value pairs. '''
def printConfigFile(config): 
    for section in config.sections():
        print(section)
        print(config.items(section))


''' Returns a ConfigParser object containing the contents of the specified .ini file, currently assumes that file is located in C:/ ... /genisys/ini-parser/ '''
def parse(file):
    file = currentDirectory.__str__() + '\\ini-parser\\' + file # Non-default
    config = configparser.ConfigParser() # Create parser object
    config.read(file) # Read contents of the INI file
    return config


def main():
    config = parse('test.ini')
    configDictionary = MakeDictionary(config, False)
    # printConfigFile(config)

if __name__ == '__main__':
    main()