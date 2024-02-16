from typing_extensions import Self, Optional, Dict
import yaml

class Inventory:
    """Manages a Yaml-formatted Ansible inventory file by keeping an in-memory "shadow" hosts file
    up to date with the on-disk representation.
    """
    instances = {}

    def __init__(self: Self, filepath: str):
        """Open a file handle and initialize the in-memory representation."""
        # create a new instance
        self.filename = filepath
        self.fd = open(filepath, 'r+', encoding='utf-8')
        self.contents = yaml.safe_load(self.fd)

        # ensure the inventory group exists
        if 'genisys' not in self.contents:
            self.contents['genisys'] = {'hosts': {}}

    def __del__(self: Self):
        """Close the file handle if this is the last remaining instance."""
        self.fd.close()

    def get(self: Self, hostname: str) -> Optional[Dict]:
        """Returns None if the host doesn't exist or the settings if it does"""
        return self.contents['genisys']['hosts'].get(hostname)

    def add_host(self: Self, hostname: str, settings: Optional[Dict] = None):
        """Adds the host to the inventory, updating the in-memory and on-disk file."""
        # Update the in-memory representation
        self.contents['genisys']['hosts'][hostname] = settings or {}

        # Truncate the current inventory file
        self.fd.seek(0)

        # Write the new invetory to disk
        yaml.dump(self.contents, self.fd)
        self.fd.flush()
