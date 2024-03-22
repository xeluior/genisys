#!/usr/bin/env python3
import ssl
import pwd
import grp
import os
import sys
import subprocess
from warnings import warn
from signal import signal, SIGTERM
from typing_extensions import Dict, TypedDict, cast
from genisys.config_parser import YAMLParser
from genisys.server.genisysinventory import GenisysInventory
from genisys.server.http import GenisysHTTPServer, GenisysHTTPRequestHandler
import genisys.server.tls
import pkg_resources
import tarfile 

DEFAULT_PORT = 15206
DEFAULT_INVENTORY = "/etc/ansible/hosts"

ServerOptions = TypedDict("ServerOptions", {
    "port": int,
    "user": str,
    "group": str,
    "working-directory": str,
    "ssl": Dict[str, str]
})

def run(config: YAMLParser):
    """Drops priviledges, creates the server (with SSL, if applicable), then waits for requests"""
    # parse config
    network = config.get_section("Network")
    server_options = cast(ServerOptions, network.get("server", {}) or {})

    # Launch meteor server
    meteor_initialization(server_options)

    # drop priviledges
    try:
        server_user = drop_priviledges(server_options)
    except PermissionError:
        warn("Unable to drop privledges to the specified user. Continuing as current user.")
        server_user = pwd.getpwuid(os.getuid())

    # change working directory
    workdir = server_options.get("working-directory", server_user.pw_dir)
    os.chdir(workdir)

    # install additional data for the server to use
    network_cfg = config.get_section("Network")
    inventory_path = network_cfg["server"]["inventory-file"]

    # create a server
    server_address = network.get('ip', '')
    server_port = server_options.get("port", DEFAULT_PORT)
    httpd = GenisysHTTPServer((server_address, server_port), GenisysInventory(inventory_path), config)

    # apply TLS if applicable
    if 'ssl' in server_options:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_cert = genisys.server.tls.get_keychain(server_options['ssl'] or {})
        ssl_context.load_cert_chain(**ssl_cert)
        httpd.socket = ssl_context.wrap_socket(httpd.socket)


    # run until SIGTERM is caught
    def sigterm_handler(*_):
        print("killed")
        del httpd.inventory
        sys.exit(SIGTERM)
    signal(SIGTERM, sigterm_handler)
    httpd.serve_forever()

    # end sigterm_handler

# end run

def drop_priviledges(config: ServerOptions) -> pwd.struct_passwd:
    """Attempts to drop the priviledges to that of the specified users, returns false on failure"""
    if 'user' not in config:
        warn("No user specified. Continuing as current user.")
        return pwd.getpwuid(os.geteuid())

    grpnam = config.get('group', config['user'])
    uid = pwd.getpwnam(config['user'])
    gid = grp.getgrnam(grpnam)

    os.setuid(uid.pw_uid)
    os.setgid(gid.gr_gid)
    return uid

# end drop_privledges

def meteor_initialization(server_config: ServerOptions):
    '''Runs Meteor as a subprocess of Genisys and 
    initializes necessary environment variables for
    Meteor. This process assumes that the user already
    has MongoDB installed and running.'''

    # Set environment variables
    os.environ['ROOT_URL'] = 'http://localhost'
    os.environ['PORT'] = '8080'
    if 'MONGO_URL' not in os.environ:
        print('MONGO_URL not found in environment variables, cancelling Meteor server.')
        return
    print('MONGO_URL found.')

    if 'CONFIG_FILE' not in os.environ:
        print('CONFIG_FILE not found in environment variables, cancelling Meteor server.')
        return
    print('CONFIG_FILE found.')

    # Make Meteor directory
    meteor_dir = os.path.join(server_config.get('working-directory'), 'meteor')
    os.makedirs(meteor_dir, exist_ok=True)

    # Get path to tar file
    tar_file_path = pkg_resources.resource_filename('genisys', 'server/external/meteor-dev.tar.gz')

    # Extract tarball Meteor build
    file = tarfile.open(tar_file_path)
    file.extractall(meteor_dir, filter='fully_trusted')
    file.close()

    # npm install and run 
    subprocess.run(['npm', 'install', '--prefix', os.path.join(meteor_dir,'bundle', 'programs', 'server'), '--unsafe-perm'], check=True)
    subprocess.run(['node', os.path.join(meteor_dir,'bundle', 'main.js')], check=True)


# end meteor_initialization
