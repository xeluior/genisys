#!/usr/bin/env bash
# Description:
#   This script uses VirtualBox as a Hypervisor to run automated tests of the
#   genisys host and client communications. It utilizes a VDI that is
#   preintalled with the nessecary prerequisites to build and run the Genisys
#   tool. SSH is used to control the Host VM for setting up the tests then a
#   recording is taken of the client VM's boot process.
# Prerequisites:
#   Features used in this script rely on Bash 5.0. The following tools must
#   also be installed and their binaries in a directory on the PATH:
#     - curl
#     - vboxmanage
#     - coreutils
# Usage
#   Parts of the script can be configured using environment variables or
#   using a .env file with SETTING=VALUE per line. The TEST_ID is set always to
#   the Epoch Seccond the test was started on. Available settings are:
#     - TMPDIR (/tmp): directory to use for caching the template VDI
#     - TEST_FOLDER_PREFIX (genisys-test): concatenated with the TEST_ID to
#       determine the folder for storing test artifacts
#     - HOST_VM_PREFIX (genisys-host): concatenated with the TEST_ID to
#       determine the name for the host VM in VirtualBox
#     - SSH_PORT (TEST_ID % 64511 + 1024): the port to forward to the host VM
#       for SSH connections
#     - CLIENT_VM_PREFIX (genisys-client): concatenated with the TEST_ID to
#       determine the name for the client VM in VirtualBox
#     - INTNET_PREFIX (genisys-intnet): concatenated with the TEST_ID to
#       determine the name of the internal network VirtualBox uses for
#       communication between the host and the client
#     - HOST_RAM (4096): Memory (in MB) allocated to the host VM
#     - HOST_CPU (2): Count of CPUs allocated to the host VM

set -ex

source .env

TEST_ID="$EPOCHSECONDS"
TMPDIR="${TMPDIR:-/tmp}"
TEMPLATE_VDI_CACHE_FILE="${TMPDIR}/genisys-host-template.vdi"
TEST_FOLDER="${PWD}/${TEST_FOLDER_PREFIX:-genisys-test}-${TEST_ID}"
HOST_VMNAME="${HOST_VM_PREFIX:-genisys-host}-${TEST_ID}"
HOST_UNAME="adam"
HOST_VDI="${TEST_FOLDER}/genisys-host.vdi"
HOST_SSH_CONF_FILE="${TEST_FOLDER}/genisys-host.ssh_config"
HOST_SSH_PORT=${SSH_PORT:-$(( ${TEST_ID} % 64511 + 1024 ))}
HOST_SSH_KEY="${PWD}/tests/ssh/id_rsa"
CLIENT_VMNAME="${CLIENT_VM_PREFIX:-genisys-client}-${TEST_ID}"
INTNET_NAME="${INTNET_PREFIX:-genisys-intnet}-${TEST_ID}"
PREINSTALLED_UBUNTU_TEMPLATE="https://genisys-testing-vbox.s3.us-east-2.amazonaws.com/genisys-test-template.vdi"

# verify the SSH key is available
if [ ! -r "${HOST_SSH_KEY}" ]; then
  echo "You do not appear to be in the genisys repo. Please run this script from the git root."
  exit 1
fi

# create the host VM
mkdir -p "${TEST_FOLDER}"
curl -o "${HOST_VDI}" "${PREINSTALLED_UBUNTU_TEMPLATE}"
vboxmanage createvm \
  --name="${HOST_VMNAME}" \
  --basefolder="${TEST_FOLDER}" \
  --default \
  --ostype="Ubuntu_64" \
  --register
vboxmanage modifyvm "${HOST_VMNAME}" \
  --nat-pf1="guestssh,tcp,localhost,${HOST_SSH_PORT},localhost,22"
vboxmanage modifyvm "${HOST_VMNAME}" \
  --nic2="intnet" \
  --cable-connected2="on" \
  --intnet2="${INTNET_NAME}" \
  --mac-address2=auto
vboxmanage storageattach "${HOST_VMNAME}" \
  --storagectl="IDE" \
  --port=0 \
  --device=0 \
  --type="hdd" \
  --medium="${HOST_VDI}" \
  --setuuid=""

