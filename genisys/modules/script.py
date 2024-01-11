from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Script(Module):

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["Scripts"] =  config.get_section("Scripts")
    #end __init__
        
    