#!/usr/bin/env bash
# Description:
#   This script uses VirtualBox as a Hypervisor to run automated tests of the
#   genisys host and client communications. It utilizes a VDI that is
#   preintalled with the nessecary prerequisites to build and run the Genisys
#   tool. SSH is used to control the Host VM for setting up the tests then a
#   recording is taken of the client VM's boot process.
# Prerequisites:
#   A single test will spin up 2 VMs with total resource usage of 12GB of RAM
#   and 4 CPU cores. Resource usage can be adjusted as described in the Usage
#   section.
#   TEST_IDs are improved with the use of bash 5.0. The following tools must
#   also be installed and their binaries in a directory on the PATH:
#     - curl
#     - vboxmanage (or VBoxManage)
#     - coreutils
#     - poetry (version 1.8+)
#     - ssh
# Usage
#   ./tests/scripts/test.sh <test name>
#
#   The test name is the name of any folder in ./tests/scripts/tests/ which
#   includes both a "setup.sh" and an "expect.sh". "setup.sh" is ran on the
#   genisys-host vm after it is online but before configuring the
#   genisys-client vm. After the script has completed, the client vm is booted.
#   TODO: when to run "expect.sh"
#   On the host VM, the built wheel is available at /app/genisys-0.1.0-py3-none-any.whl
#   Any files put in the data/ subdir of the test directory are also included
#   in the /app/ dir on the host VM.
#
#   Parts of the script can be configured using environment variables or
#   using a .env file with SETTING=VALUE per line. The TEST_ID is set always to
#   the Epoch Seccond the test was started on (in Bash 5+) or a random number
#   less than 32,767 on lower versions. Available settings are:
#     - TMPDIR (/tmp): directory to use for caching the template VDI
#     - TEST_FOLDER_PREFIX ($PWD/genisys-test): concatenated with the TEST_ID to
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
#     - HOST_RAM (8192): Memory (in MB) allocated to the host VM
#     - HOST_CPU (2): Count of CPUs allocated to the host VM
#     - CLIENT_RAM (4096): Memory (in MB) allocated to the client VM
#     - CLIENT_CPU (2): Count of CPUs allocated to the client VM
#     - VBOXMANAGE (vboxmanage or VBoxManage): set the path to the installed
#       vboxmanage binary

set -ex

[ -r .env ] && source .env

TEST_ID="${EPOCHSECONDS:-$RANDOM}"
TEST_NAME="${1:?'No test specified'}"
TEST_PATH="./tests/scripts/tests/${TEST_NAME}"
TMPDIR="${TMPDIR:-/tmp}"
TEMPLATE_VDI_CACHE_FILE="${TMPDIR}/genisys-host-template.vdi"
TEST_FOLDER="${TEST_FOLDER_PREFIX:-"${PWD}/genisys-test"}-${TEST_ID}"
SHARED_FOLDER="${TEST_FOLDER}/app"
HOST_VMNAME="${HOST_VM_PREFIX:-genisys-host}-${TEST_ID}"
HOST_UNAME='adam'
HOST_VDI="${TEST_FOLDER}/genisys-host.vdi"
HOST_SSH_CONF_FILE="${TEST_FOLDER}/genisys-host.ssh_config"
HOST_SSH_PORT=${SSH_PORT:-$(( ${TEST_ID} % 64511 + 1024 ))}
HOST_SSH_KEY="${PWD}/tests/ssh/id_rsa"
CLIENT_VMNAME="${CLIENT_VM_PREFIX:-genisys-client}-${TEST_ID}"
CLIENT_VDI_NAME="${TEST_FOLDER}/${CLIENT_VMNAME}/${CLIENT_VMNAME}.vdi"
INTNET_NAME="${INTNET_PREFIX:-genisys-intnet}-${TEST_ID}"
PREINSTALLED_UBUNTU_TEMPLATE='https://genisys-testing-vbox.s3.us-east-2.amazonaws.com/genisys-test-template.vdi'
VBOXMANAGE=${VBOXMANAGE:-$(which vboxmanage || which VBoxManage)}

# verify the SSH key is available
if [ ! -r "${HOST_SSH_KEY}" ]; then
  echo 'You do not appear to be in the genisys repo. Please run this script from the git root.'
  exit 1
fi
chmod 0600 "${HOST_SSH_KEY}"

# build the package
mkdir -p "${TEST_FOLDER}"
poetry build \
  --format=wheel \
  --output="${SHARED_FOLDER}"

# add additional test files to the shared folder
cp "${TEST_PATH}/data"/* "${SHARED_FOLDER}"

# cache the template VDI download
if [ ! -r "${TEMPLATE_VDI_CACHE_FILE}" ]; then
  curl -o "${TEMPLATE_VDI_CACHE_FILE}" "${PREINSTALLED_UBUNTU_TEMPLATE}"
fi

# create the host VM
cp "${TEMPLATE_VDI_CACHE_FILE}" "${HOST_VDI}"
"${VBOXMANAGE}" createvm \
  --name="${HOST_VMNAME}" \
  --basefolder="${TEST_FOLDER}" \
  --default \
  --ostype='Ubuntu_64' \
  --register
"${VBOXMANAGE}" modifyvm "${HOST_VMNAME}" \
  --memory=${HOST_RAM:-8192} \
  --cpus=${HOST_CPU:-2}
"${VBOXMANAGE}" modifyvm "${HOST_VMNAME}" \
  --nat-pf1="guestssh,tcp,localhost,${HOST_SSH_PORT},localhost,22"
"${VBOXMANAGE}" modifyvm "${HOST_VMNAME}" \
  --nic2='intnet' \
  --cable-connected2=on \
  --intnet2="${INTNET_NAME}" \
  --mac-address2=auto
"${VBOXMANAGE}" storageattach "${HOST_VMNAME}" \
  --storagectl='IDE' \
  --port=0 \
  --device=0 \
  --type='hdd' \
  --medium="${HOST_VDI}" \
  --setuuid=''
"${VBOXMANAGE}" sharedfolder add "${HOST_VMNAME}" \
  --name='app' \
  --hostpath="${SHARED_FOLDER}" \
  --readonly \
  --automount \
  --auto-mount-point='/app'
"${VBOXMANAGE}" startvm "${HOST_VMNAME}" \
  --type='headless'

# configure ssh for the guest
# simplifies connecting to host and port
# ignores condition for accepting host fingerprint
cat <<SSH >"${HOST_SSH_CONF_FILE}"
Host ${HOST_VMNAME}
  User ${HOST_UNAME}
  Port ${HOST_SSH_PORT}
  IdentityFile ${HOST_SSH_KEY}
  HostName localhost
  ConnectTimeout 3
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
SSH
host-ssh() {
  ssh -F "${HOST_SSH_CONF_FILE}" "${HOST_VMNAME}" $@
}

# wait for SSH to be available
while ! host-ssh echo 'Connected' 2>/dev/null; do :; done

# install the package
host-ssh sh <"${TEST_PATH}/setup.sh"

# setup the client VM
"${VBOXMANAGE}" createvm \
  --name="${CLIENT_VMNAME}" \
  --basefolder="${TEST_FOLDER}" \
  --default \
  --ostype='Debian_64' \
  --register
"${VBOXMANAGE}" createmedium disk \
  --filename="${CLIENT_VDI_NAME}" \
  --size=8096 \
  --format='VDI'
"${VBOXMANAGE}" storageattach "${CLIENT_VMNAME}" \
  --storagectl='IDE' \
  --port=0 \
  --device=0 \
  --type='hdd' \
  --medium="${CLIENT_VDI_NAME}"
"${VBOXMANAGE}" modifyvm "${CLIENT_VMNAME}" \
  --memory=${CLIENT_RAM:-4096} \
  --cpus=${CLIENT_CPU:-2}
"${VBOXMANAGE}" modifyvm "${CLIENT_VMNAME}" \
  --bios-boot-menu='disabled' \
  --boot1='disk' \
  --boot2='net'
"${VBOXMANAGE}" modifyvm "${CLIENT_VMNAME}" \
  --nic1="intnet" \
  --cable-connected1=on \
  --intnet1="${INTNET_NAME}" \
  --mac-address1=auto
"${VBOXMANAGE}" modifyvm "${CLIENT_VMNAME}" \
  --recording=on \
  --recording-screens=all \
  --recording-file="${TEST_FOLDER}/client.mp4" \
  --recording-video-fps=10
"${VBOXMANAGE}" startvm "${CLIENT_VMNAME}" \
  --type='headless'

