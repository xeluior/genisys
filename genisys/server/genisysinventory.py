import json

from pymongo import MongoClient
from typing import Optional, Dict
import re

class GenisysInventory:
    """Handles operations relating to the management of a MongoDB collection
    of all the client machines booted through Genisys, and to store metadata
    associated with each client"""

    HOSTNAME_PREFIX = "genisys"

    def __init__(self, db_uri: str, db_name: str, collection_name: str):
        # Connect to MongoDB without authentication
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # Ensure that the collection structure exists
        if self.collection.count_documents({}) == 0:
            # Initialize the collection with a basic structure if needed
            self.collection.insert_one({"genisys": {"hosts": []}})

    def __del__(self):
        """Close the MongoDB connection."""
        self.client.close()

    def get_host(self, host: str) -> Optional[Dict]:
        """Searches the running inventory for a specific hostname,
        if not found returns None"""
        result = self.collection.find_one({"hostname": host})
        return result

    def add_host(self, host) -> str:
        """Adds a host to the running inventory and updates the hostname
        in the inventory for later assignment."""
        if not isinstance(host, dict):
            host_dict = json.loads(host)
        else:
            host_dict = host

        # Assign the next hostname
        host_dict["hostname"] = self.get_next_hostname()

        # Set provisioned status to false
        host_dict["provisioned"] = False

        # Insert the new host document directly into the collection
        self.collection.insert_one(host_dict)

        return host_dict["hostname"]

    def get_next_hostname(self):
        # Attempt to find the highest current hostname number
        regex_pattern = "^genisys(\d+)$"  # Pattern to extract the numeric part
        last_host = self.collection.find_one(
            {"hostname": {"$regex": regex_pattern}},
            sort=[("hostname", -1)]
        )
        if last_host:
            # Extract the number from the hostname, increment it, and pad with zeros
            match = re.search(regex_pattern, last_host["hostname"])
            if match:
                last_num = int(match.group(1))
                new_num = last_num + 1
            else:
                new_num = 1  # Fallback if regex match fails
        else:
            new_num = 1

        # Adjust the zero padding based on your maximum expected number of hosts
        return f"genisys{str(new_num).zfill(5)}"


