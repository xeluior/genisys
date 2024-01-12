from pathlib import Path
from typing_extensions import Self
from os import rename

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Script(Module):

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["scripts"] = config.get_section("Scripts")
        self.config["network"] = config.get_section("Network")
    #end __init__

    def move_files(self: Self):
        #Location of scripts in genisys directory
        source = Path("/genisys/scripts") #This will need fixed 
        #Location of FTP directory on genisys host 
        destination = Path(self.config["network"]["ftp"]["directory"])
        
        rename(source, destination)
    #end move_files

# def main():
#     script = Script(YAMLParser('C:/Users/greeht01/Desktop/genisys/documentation/example.yml'))
#     script.move_files()

# if __name__ == '__main__':
#     main()
