import configparser 
import pathlib

currentDirectory = pathlib.Path().resolve() # Returns windowsPath obj representing working directory (\genisys\)

def parse(filename = currentDirectory.__str__() + '\\ini-parser\\test.ini'):
    config = configparser.ConfigParser() # Create parser object

    config.read(filename) # Read contents of the INI file

    print("Filename: " + filename)
    print(config.sections()) 

def main():
    parse()

if __name__ == '__main__':
    main()