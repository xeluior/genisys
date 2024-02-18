import json
from typing_extensions import Self, Optional, Dict


class GenisysInventory:
    """Handles operations relating to the creation of a temporary inventory
    file of all of the client machines booted through Genisys, and to store
    metadata associated with each client"""

    HOSTNAME_PREFIX = "genisys"

    def __init__(self: Self, filepath: str):
        self.filepath = filepath
        self.fd = open(filepath, "w+", encoding="utf-8")

        # Load any host entries from the past
        try:
            self.running_inventory = json.load(self.fd)
        except json.decoder.JSONDecodeError:
            self.running_inventory = {}

        # Ensure that dictionary structure exists
        if "genisys" not in self.running_inventory:
            self.running_inventory["genisys"] = {"hosts": []}

    # end __init__

    def __del__(self: Self):
        """Close the file handle if this is the last remaining instance."""
        self.fd.close()

    # end __del__

    def get_host(self: Self, host: str) -> Optional[Dict]:
        """Searches the running inventory for a specifc hostname,
        if not found returns None"""
        host_list = self.running_inventory["genisys"]["hosts"]

        for element in host_list:
            if element["hostname"] == host:
                return element

        return None

    # end get_host

    def add_host(self: Self, host):
        """Adds a host to the running inventory, takes in
        the JSON body of a request and adds it to the running
        and on-disk memory. It also updates the hostname in the
        inventory for later assignment."""
        if not isinstance(host, dict):
            host_dict = json.loads(host)
        else:
            host_dict = host

        host_dict["hostname"] = self.get_next_hostname()

        self.running_inventory["genisys"]["hosts"].append(host_dict)
        self.update_file()

    # end add_host

    def update_file(self: Self):
        """Writes the current running inventory to the
        on-disk file"""
        self.fd.seek(0)
        json.dump(self.running_inventory, self.fd)

        self.fd.flush()

    # end update_file

    def get_next_hostname(self: Self) -> str:
        """Returns the next hostname by checking the inventory's most
        recent entry and incrementing numeric component at the end"""
        try:
            last_entry = self.running_inventory["genisys"]["hosts"][-1]
        except IndexError:
            # If there are no previous entries in the inventory file
            return self.HOSTNAME_PREFIX + "1"

        new_value = int(last_entry["hostname"][7:]) + 1

        return self.HOSTNAME_PREFIX + str(new_value)

    # end get_next_hostname


# end GenisysInventory
