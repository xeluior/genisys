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
import importlib.util
import tarfile
import dotenv
from pathlib import Path



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

    #Connect to database
    db_uri = os.getenv("MONGO_URL") # Adjust based on your MongoDB setup
    db_name = "local"  # The database name
    collection_name = "ClientsCollection"  # The collection name

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

    # create a server
    server_address = network.get('ip', '')
    server_port = server_options.get("port", DEFAULT_PORT)
    inventory = GenisysInventory(db_uri, db_name, collection_name)
    httpd = GenisysHTTPServer((server_address, server_port), inventory, config)
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

    if 'GITHUB_RUNNER' in os.environ:
        return

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

    os.initgroups(uid.pw_name, gid.gr_gid)
    os.setgid(gid.gr_gid)
    os.setuid(uid.pw_uid)
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
        print('CONFIG_FILE not found in environment variables, defaulting to /etc/genisys.yaml.')
    else:
        print('CONFIG_FILE env var found.')

    # Make Meteor directory
    meteor_dir = os.path.join(server_config.get('working-directory'), 'meteor')
    os.makedirs(meteor_dir, exist_ok=True)

    # Get path to tar file
    package_location = importlib.util.find_spec('genisys').origin
    tar_file_path = Path(package_location[:package_location.rfind('/')], 'server/external/meteor-dev.tar.gz')
    
    #If in github action, run as test then return
    if 'GITHUB_RUNNER' in os.environ:
        print("Running meteor as test.")
        old_cwd = os.getcwd()
        meteor_dev_dir = Path(package_location[:package_location.rfind('genisys/')], 'meteor-dev')
        os.chdir(meteor_dev_dir) 
        result = ""
        try:
            result = subprocess.run(['meteor', 'test', '--driver-package', 'meteortesting:mocha', '--once', '--full-app', '--allow-superuser '], check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(repr(e))
            raise Exception("Error running Meteor test")
            
        os.chdir(old_cwd)
        return


    # Extract tarball Meteor build
    file = tarfile.open(tar_file_path)
    file.extractall(meteor_dir, filter='fully_trusted')
    file.close()

    # npm install and run 
    subprocess.run(['npm', 'install', '--prefix', os.path.join(meteor_dir,'bundle', 'programs', 'server'), '--unsafe-perm'], check=True)
    subprocess.Popen(['node', os.path.join(meteor_dir,'bundle', 'main.js')], stderr=subprocess.STDOUT)
    print('Done running Meteor initialization.')


# end meteor_initialization
