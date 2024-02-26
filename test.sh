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

set -ex

TEST_ID="$EPOCHSECONDS"
VBOX_GROUP="/genisys-tests/${TEST_ID}"
TEST_FOLDER="${PWD}/genisys-test-${TEST_ID}"
HOST_VMNAME="genisys-host-${TEST_ID}"
HOST_VDI="${TEST_FOLDER}/genisys-host.vdi"
HOST_SSH_PORT=$(( ${TEST_ID} % 64511 + 1024 ))
CLIENT_VMNAME="genisys-client-${TEST_ID}"
INTNET_NAME="genisys-intnet-${TEST_ID}"
PREINSTALLED_UBUNTU_TEMPLATE="https://genisys-testing-vbox.s3.us-east-2.amazonaws.com/genisys-test-template.vdi"

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

