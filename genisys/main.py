#!/usr/bin/env

import argparse
import subprocess
import genisys.modules.netplan as net
import genisys.modules.preseed as ps
import genisys.modules.nat as nt
import genisys.modules.kernelparameter as kp
import genisys.configParser as cp

def validate(modules):
    for module in modules:
        if not module.validate():
            print(f"Error in {module.__class__.__name__} configuration!")
        else:
            print(f"{module.__class__.__name__} configuration is valid!")

def install_config(file, root="/"):
    print(f"Installing config file: {file} with root at {root}")
    # netplan
    netplan = net.Netplan()
    netplan.install(root)

    # preseed
    preseed = ps.Preseed()
    preseed.install(root)

    # nat
    nat = nt.Nat()
    nat.install(root)

    # kernelparameter
    kernelParameter = kp.KernelParameter()     
    kernelParameter.install(root)

def daemon():
    print("Starting daemon...")

    raise NotImplementedError
    # TODO: Implement the daemon logic here

def run(subcommand, args, module):
    # Config Parser
    yamlParser = cp.YAMLParser()

    # netplan
    netplan = net.Netplan(args, yamlParser)

    # preseed
    preseed = ps.Preseed(args, yamlParser)

    # nat
    nat = nt.Nat(args, yamlParser)

    # kernelparameter
    kernelParameter = kp.KernelParameter(args, yamlParser)

    # setup commands
    modulesList = [netplan, preseed, nat, kernelParameter]
    for mod in modulesList:
        # function setup_commands returns list
        for command in mod.setup_commands:
            subprocess.run(command)

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
