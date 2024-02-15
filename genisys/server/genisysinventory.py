from typing_extensions import Self
import json


class GenisysInventory:
    """Handles operations relating to the creation of a temporary inventory
    file of all of the client machines booted through Genisys, and to store
    metadata associated with each client"""

    def __init__(self: Self, filepath: str):
        self.filepath = filepath
        self.fd = open(filepath, "r+", encoding="utf-8")
        # Load any host entries from the past
        self.running_inventory = json.load(self.fd)

    # end __init__

    def __del__(self: Self):
        """Close the file handle if this is the last remaining instance."""
        self.fd.close()

    # end __del__

    def get_host(self: Self):
        """Searches the running inventory for a specifc host,
        if not found returns None"""
        pass

    # end get_host

    def add_host(self: Self, host):
        """Adds a host to the running inventory"""
        pass

    # end add_host

    def update_file(self: Self):
        """Writes the current running inventory to the
        on-disk file"""
        pass

    # end update_file

# end GenisysInventory
