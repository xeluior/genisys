

if __name__ == "__main__":
    import json
    from genisys.server import GenisysInventory

    # MongoDB connection details
    db_uri = "mongodb://localhost:3001"
    db_name = "meteor"
    collection_name = "ClientsCollection"

    # Instantiate the GenisysInventory
    inventory = GenisysInventory(db_uri, db_name, collection_name)

    for i in range(20):
        test_host = {
            "ip": "192.168.1.111",
            "key": "value1",
            "key2": "value2"
        }
        print("Testing GenisysInventory with MongoDB...")

        # Add a host
        print("\nAdding a host...")
        hostname = inventory.add_host(test_host)
        print(f"Added host with hostname: {hostname}")

        # Retrieve the added host
        print("\nRetrieving the added host...")
        retrieved_host = inventory.get_host(hostname)
        print(retrieved_host)

