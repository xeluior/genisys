from typing_extensions import Self
import yaml

class Inventory:
    """Manages a Yaml-formatted Ansible inventory file by keeping an in-memory "shadow" hosts file
    up to date with the on-disk representation. Acts as a pseudo-singleton allowing only one
    instance per filepath to exist.
    """
    instances = {}

    def __init__(self: Self, filepath: str):
        """Open a file handle and initialize the in-memory representation."""
        # check if a copy of this file is already in memory
        if filepath in Inventory.instances:
            this = Inventory.instances[filepath]
            this['count'] += 1
            return this['instance']

        # create a new instance
        self.filename = filepath
        self.fd = open(filepath, 'r+', encoding='utf-8')
        self.contents = yaml.safe_load(self.fd)
        Inventory.instances[filepath] = {
            'count': 1,
            'instance': self
        }
        
        # ensure the inventory group exists
        if 'genisys' not in self.contents:
            self.contents['genisys'] = {'hosts': {}}

    def __del__(self: Self):
        """Close the file handle if this is the last remaining instance."""
        this = Inventory.instances[self.filename]
        this['count'] -= 1
        if this['count'] == 0:
            self.fd.close()

    def add_host(self: Self, hostname: str):
        """Adds the host to the inventory, updating the in-memory and on-disk file."""
        # Update the in-memory representation
        self.contents['genisys']['hosts'][hostname] = None

        # Truncate the current inventory file
        self.fd.seek(0)

        # Write the new invetory to disk
        yaml.dump(self.contents, self.fd)
        self.fd.flush()

