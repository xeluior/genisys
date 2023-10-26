import argparse
import genisys.modules.netplan as net
import genisys.modules.preseed as ps
import genisys.modules.nat as nt
#from modules.base import any modules

def validate(modules):
    for module in modules:
        if not module.validate():
            print(f"Error in {module.__class__.__name__} configuration!")
        else:
            print(f"{module.__class__.__name__} configuration is valid!")

def install_config(file, root="/"):
    print(f"Installing config file: {file} with root at {root}")

    raise NotImplementedError
    # TODO: Implement the installation logic here

def generate_config(file, root="/"):
    print(f"Generating config file: {file} at directory {root}")

    raise NotImplementedError
    # TODO: Implement the generate logic here

def daemon():
    print("Starting daemon...")

    raise NotImplementedError
    # TODO: Implement the daemon logic here

def run(subcommand, args, module):

    #netplan
    netplan = net.Netplan(args)

    #preseed
    preseed = ps.Preseed(args)

    #nat
    nat = nt.Nat(args)

    if subcommand == "validate":
        validate(module)
    elif subcommand == "install":
        install_config(args.file, args.root)


def main():
    parser = argparse.ArgumentParser(description="Config File Management Tool")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate the configuration file.")
    install_parser = subparsers.add_parser("install", help="Install the configuration files.")
    generate_parser = subparsers.add_parser("generate", help="Generate the configuration files.")
    daemon_parser = subparsers.add_parser("daemon", help="Monitor the config file for changes.")
 
    # Flags
    for subparser in [validate_parser, install_parser, generate_parser]:
        subparser.add_argument("-f","--file", type=str, default="default_config.cfg", help="Specify input configuration file.")

    args = parser.parse_args()

    # TODO: Instantiate modules here
    modules = [] # Example: modules = [NetworkModule(), FirewallModule()]
    
    run(args.command, args, modules)

if __name__ == "__main__":
    main()
