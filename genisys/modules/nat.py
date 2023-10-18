from typing import Self
from pathlib import Path

from . import base
from typing import Self
from pathlib import Path
'''
Their Genisys repo did it by setting the iptables rules then using netfilter-persistent to save the configuration. 
Basically we want to skip the "running iptables commands" step and just generate the iptables rules files into the right directory.
I believe there is also a kernel parameter that needs set to forward instead of dropping requests. 
That may technically need to be a seperate module the way our architecture is, but it should be simple enough to fit under this task
My VM put the iptables rules into the /etc/iptables/rule.v4 file if that helps

https://github.com/mieweb/GeniSys
'''

class nat(base.Module):
    NAT_DIR='/etc/sysctl.conf'
    
    def __init__(self: Self, config: dict):
        self.config = config
    # end __init__